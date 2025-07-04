"""
Map scene implementation.
"""

from collections.abc import Callable, Generator, Iterable
from dataclasses import field, replace
from functools import cached_property
from heapq import merge
from itertools import chain
from pathlib import Path
from typing import Any, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_on_screen import (
    NpcOnScreen,
)
from nextrpg.character.npc_spec import MovingNpcSpec, StaticNpcSpec
from nextrpg.character.npcs import Npcs
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config import ResizeMode, config, initial_config
from nextrpg.core import Millisecond, Pixel, Size
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen
from nextrpg.event.move import Move
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.logger import Logger
from nextrpg.model import instance_init, register_instance_init
from nextrpg.scene.map_helper import (
    LayerTileBottomAndDrawOnScreen,
    MapHelper,
    get_polygon,
)
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene

logger = Logger("MapScene")


def _init_player(self: MapScene) -> PlayerOnScreen:
    player = self._map_helper.get_object(self.player_coordinate_object)
    return PlayerOnScreen(
        character=self.initial_player_drawing,
        coordinate=Coordinate(player.x, player.y),
        collisions=self._map_helper.collisions,
    )


@register_instance_init
class MapScene(Scene):
    """
    A scene implementation that represents a game map loaded from Tiled TMX.

    Handles rendering of map layers, character movement with collisions,
    and proper depth sorting of foreground elements relative to the player.

    Arguments:
        `tmx_file`: Path to the Tiled TMX file to load.

        `player_drawing`: Character drawing representing the player.

        `player_coordinate_object`: Name of the object to use as the player.
            Default to `None` to use the `config().map.player`.

        `moves`: List of move objects to trigger when the player enters a new
            map.
    """

    tmx_file: Path
    initial_player_drawing: CharacterDrawing
    player_coordinate_object: str
    moves: list[Move] = field(default_factory=list)
    static_npc_specs: list[StaticNpcSpec] = field(default_factory=list)
    moving_npc_specs: list[MovingNpcSpec] = field(default_factory=list)
    _player: PlayerOnScreen = instance_init(_init_player)
    _npcs: Npcs = instance_init(
        lambda self: Npcs(
            map_helper=self._map_helper,
            static_npc_specs=self.static_npc_specs,
            moving_npc_specs=self.moving_npc_specs,
        )
    )
    _current_event: Generator[Callable[[Self], Scene], None, None] | None = None
    _current_value: Any = None

    @cached_property
    @override
    def draw_on_screens(self) -> list[DrawOnScreen]:
        """
        Generate the complete list of drawable elements for the map scene.

        Combines background elements, depth-sorted foreground elements with the
        player character, and any debug visuals from the player character.

        Returns:
            `list[DrawOnScreen]`: The complete list of drawable elements in the
            correct rendering order.
        """
        draws = chain(
            self._map_helper.background,
            self._foreground_and_characters,
            self._map_helper.above_character,
            self._collision_visuals,
        )
        return [d + self._player_offset for d in draws]

    @override
    def event(self, event: PygameEvent) -> Scene:
        """
        Process input events for the map scene.

        Delegates event handling to the player character and returns an
        updated scene with the new player state.

        Arguments:
            `event`: The pygame event to process.

        Returns:
            `Scene`: The updated scene after processing the event.
        """
        return replace(self, _player=self._player.event(event))

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        """
        Update the map scene state for a single game step/frame.

        Updates the player character's position and animation state based on the
        elapsed time since the last frame.

        Arguments:
            `time_delta`: The time that has passed since the last update.

        Returns:
            `Scene`: The updated scene after the time step.
        """
        if self._current_event:
            try:
                return self._current_event.send(self._current_value)(
                    self._current_event, self
                )
            except StopIteration:
                obj = self._map_helper.get_object(self.player_coordinate_object)
                return replace(
                    self,
                    _player=replace(
                        self._player, coordinate=Coordinate(obj.x, obj.y)
                    ),
                    _current_event=None,
                )

        player = self._player.tick(time_delta)
        logger.debug("Player {player.coordinate}")
        if moved := self._move_to_scene(player):
            return moved

        if npc := self._collided_npc:
            logger.debug("Collied with {npc.name}")
            generator = npc.event_spec(player, npc, self._map_helper)
            return next(generator)(generator, self)

        return replace(self, _player=player, _npcs=self._npcs.tick(time_delta))

    @cached_property
    def _collided_npc(self) -> NpcOnScreen | None:
        collided = (n for n in self._npcs.list if self._collide_with_player(n))
        return next(collided, None)

    def _collide_with_player(self, npc: NpcOnScreen) -> bool:
        return npc.draw_on_screen.rectangle.collide(
            self._player.draw_on_screen.rectangle
        )

    @cached_property
    def _foreground_and_characters(self) -> Iterable[DrawOnScreen]:
        foregrounds = (
            LayerTileBottomAndDrawOnScreen(i, bottom, draw)
            for i, layer in enumerate(self._map_helper.foreground)
            for bottom, draw in layer
        )
        characters = [self._player] + self._npcs.list
        bottom_and_draw = sorted(
            map(self._map_helper.layer_bottom_and_draw, characters)
        )
        layers = merge(foregrounds, bottom_and_draw)
        return (draw for _, _, draw in layers)

    @cached_property
    def _player_offset(self) -> Coordinate:
        player = self._player.draw_on_screen.rectangle.center
        map_width, map_height = self._map_helper.map_size
        gui_width, gui_height = _gui_size()
        left_offset = _offset(player.left, gui_width, map_width)
        top_offset = _offset(player.top, gui_height, map_height)
        offset = Coordinate(left_offset, top_offset)
        logger.debug("Player offset {offset}")
        return offset

    def _move_to_scene(self, player: CharacterOnScreen) -> Scene | None:
        moved = (m for move in self.moves if (m := self._move(player, move)))
        return next(moved, None)

    def _move(self, player: CharacterOnScreen, move: Move) -> Scene | None:
        move_poly = get_polygon(
            self._map_helper.get_object(move.trigger_object)
        )
        return (
            TransitionScene(self, move.to_scene(player.character))
            if player.draw_on_screen.rectangle.collide(move_poly)
            else None
        )

    @cached_property
    def _collision_visuals(self) -> list[DrawOnScreen]:
        if not (debug := config().debug):
            return []
        return [
            c.fill(debug.collision_rectangle_color)
            for c in self._map_helper.collisions
        ]

    @cached_property
    def _map_helper(self) -> MapHelper:
        return MapHelper(self.tmx_file)


def _offset(player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis


def _gui_size() -> Size:
    match config().gui.resize_mode:
        case ResizeMode.SCALE:
            return initial_config().gui.size
        case ResizeMode.KEEP_NATIVE_SIZE:
            return config().gui.size
    raise ValueError(f"Invalid resize mode {config().gui.resize_mode}")
