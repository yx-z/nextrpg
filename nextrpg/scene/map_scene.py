"""
Map scene implementation.
"""

from dataclasses import dataclass, field, replace
from functools import cached_property
from os import PathLike
from typing import Callable, NamedTuple, OrderedDict, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterSpec
from nextrpg.character.moving_npc import MovingNpcOnScreen
from nextrpg.character.npcs import EventfulScene, NpcOnScreen, NpcSpec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config import config
from nextrpg.draw.coordinate import Coordinate
from nextrpg.core import Millisecond, Pixel
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.gui.area import gui_size
from nextrpg.logger import Logger
from nextrpg.model import dataclass_with_instance_init, instance_init
from nextrpg.scene.map_helper import MapHelper, get_polygon
from nextrpg.scene.scene import Scene
from nextrpg.scene.static_scene import StaticScene
from nextrpg.scene.transition_triple import TransitionTriple
from nextrpg.timepoint import Timepoint, get_timepoint

logger = Logger("MapScene")


def _init_player(self: MapScene) -> PlayerOnScreen:
    return self.init_player(self.player_spec)


def _init_npcs(self: "MapScene") -> tuple[NpcOnScreen, ...]:
    return tuple(self._init_npc(n) for n in self.npc_specs)


@dataclass_with_instance_init
class MapScene(EventfulScene):
    """
    A scene implementation that represents a game map loaded from Tiled TMX.

    Handles rendering of map layers, character movement with collisions,
    and proper depth sorting of foreground elements relative to the player.

    Arguments:
        `tmx_file`: Path to the Tiled TMX file to load.

        `player_drawing`: Character drawing representing the player.

        `player_coordinate_object`: Name of the object to use as the player.
            Default to `None` to use the `config().map.player`.

        `moves`: Tuple of move objects to trigger when the player enters a new
            map.
    """

    tmx_file: PathLike | str
    player_spec: CharacterSpec
    moves: tuple[Move, ...] = field(default_factory=tuple)
    npc_specs: tuple[NpcSpec, ...] = field(default_factory=tuple)
    collision_visuals: tuple[DrawOnScreen, ...] = instance_init(
        lambda self: self._collision_visuals
    )
    npcs: tuple[NpcOnScreen, ...] = instance_init(_init_npcs)
    player: PlayerOnScreen = instance_init(_init_player)

    @cached_property
    def map_helper(self) -> MapHelper:
        return MapHelper(self.tmx_file)

    def init_player(self, player_spec: CharacterSpec) -> PlayerOnScreen:
        player = self.map_helper.get_object(player_spec.name)
        return PlayerOnScreen(
            character=player_spec.character,
            coordinate=Coordinate(player.x, player.y),
            collisions=self.map_helper.collisions,
            spec=player_spec,
        )

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        return self._move_to_scene or super().tick(time_delta)

    @cached_property
    def _foreground_and_characters(self) -> tuple[DrawOnScreen, ...]:
        characters = (self.player,) + self.npcs
        layer_bottom_draws = sorted(
            draw
            for character in characters
            for draw in self.map_helper.layer_bottom_and_draw(character)
        )
        foregrounds = [t for layer in self.map_helper.foreground for t in layer]
        layers = sorted(foregrounds + layer_bottom_draws, key=lambda x: x[:2])
        return tuple(draw for _, _, draw in layers)

    @cached_property
    @override
    def draw_on_screen_shift(self) -> Coordinate:
        player = self.player.draw_on_screen.rectangle.center
        map_width, map_height = self.map_helper.map_size
        gui_width, gui_height = gui_size()
        left_shift = _shift(player.left, gui_width, map_width)
        top_shift = _shift(player.top, gui_height, map_height)
        shift = Coordinate(left_shift, top_shift)
        logger.debug(
            t"Player {self.player.coordinate} Shift {shift}", duration=None
        )
        return shift

    @cached_property
    def _move_to_scene(self) -> TransitionTriple | None:
        for move in self.moves:
            if m := self._move(move):
                return m
        return None

    def _move(self, move: Move) -> TransitionTriple | None:
        move_poly = get_polygon(self.map_helper.get_object(move.trigger_object))
        if self.player.draw_on_screen.rectangle.collide(move_poly):
            return move.to_scene(self, self.player.character)
        return None

    @cached_property
    def _collision_visuals(self) -> tuple[DrawOnScreen, ...]:
        if not (debug := config().debug):
            return ()
        collisions = tuple(
            c.fill(debug.collision_rectangle_color)
            for c in self.map_helper.collisions
        )
        npc_paths = tuple(
            n.path.line(debug.npc_path_color)
            for n in self.npcs
            if isinstance(n, MovingNpcOnScreen)
        )
        return collisions + npc_paths

    def _init_npc(self, spec: NpcSpec) -> NpcOnScreen:
        obj = self.map_helper.get_object(spec.name)
        coord = Coordinate(obj.x, obj.y)
        if poly := get_polygon(obj):
            return MovingNpcOnScreen(coordinate=coord, path=poly, spec=spec)
        return NpcOnScreen(coordinate=coord, spec=spec)

    @cached_property
    @override
    def draw_on_screens_before_shift(self) -> tuple[DrawOnScreen, ...]:
        return (
            self.map_helper.background
            + self._foreground_and_characters
            + self.map_helper.above_character
            + self.collision_visuals
        )


@dataclass(frozen=True)
class Move:
    """
    Move event from the current scene to another.

    Attributes:
        `to_object`: Name of the object to move to.

        `trigger_object`: Name of the object to trigger the move.

        `next_scene`: Callable to get the next scene.
    """

    to_object: str
    trigger_object: str
    next_scene: (
        Callable[[CharacterSpec | None], MapScene]
        | Callable[[CharacterSpec], MapScene]
    )

    def to_scene(
        self, from_scene: MapScene, character: CharacterDrawing
    ) -> TransitionTriple:
        """
        Move to another scene.

        Arguments:
            `from_scene`: The current scene.

            `character`: The character to appear in the next scene.

        Returns:
            `TransitionScene`: The transition to the next scene.
        """
        spec = CharacterSpec(name=self.to_object, character=character)
        now = get_timepoint()

        if not (tmx := _tmxs.get(self.next_scene)):
            next_scene = self.next_scene(spec)
            tmx = str(next_scene.tmx_file)

        if timed_scene := _scenes.get(tmx):
            timepoint, scene = timed_scene
            time_delta = now - timepoint
            player = scene.init_player(spec)
            to_scene = replace(scene, player=player).tick_without_event(
                time_delta
            )
        else:
            to_scene = self.next_scene(spec)

        while _scenes and len(_scenes) >= config().resource.map_cache_size:
            _scenes.popitem(last=False)
        _scenes[str(from_scene.tmx_file)] = _TimedScene(now, from_scene)

        while _tmxs and len(_tmxs) >= config().resource.map_cache_size:
            _tmxs.popitem(last=False)
        _tmxs[self.next_scene] = tmx

        return TransitionTriple(
            from_scene=from_scene, intermediary=StaticScene(), to_scene=to_scene
        )


class _TimedScene(NamedTuple):
    time: Timepoint
    scene: MapScene


def _shift(player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis


_tmxs = OrderedDict[Callable[..., MapScene], str]()
_scenes = OrderedDict[str, _TimedScene]()
