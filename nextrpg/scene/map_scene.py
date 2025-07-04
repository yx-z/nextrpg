"""
Map scene implementation.
"""

from collections.abc import Iterable
from dataclasses import field, replace
from functools import cached_property, singledispatchmethod
from heapq import merge
from itertools import chain
from os import PathLike
from pathlib import Path
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npcs import NpcSpec, Npcs, RpgEventGenerator
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config import config
from nextrpg.core import Millisecond, Pixel
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen
from nextrpg.event.move import Move
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.gui import gui_size
from nextrpg.logger import Logger
from nextrpg.model import instance_init, register_instance_init
from nextrpg.scene.eventful_scene import EventfulScene
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
class MapScene[T](EventfulScene):
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

    tmx_file: PathLike | str
    initial_player_drawing: CharacterDrawing
    player_coordinate_object: str
    moves: list[Move] = field(default_factory=list)
    npcs: list[NpcSpec] = field(default_factory=list)
    _player: PlayerOnScreen = instance_init(_init_player)
    _npcs: Npcs = instance_init(
        lambda self: Npcs(map_helper=self._map_helper, specs=self.npcs)
    )

    @cached_property
    @override
    def draw_on_screens(self) -> list[DrawOnScreen]:
        return (
            self._map_helper.background
            + self._foreground_and_characters
            + self._map_helper.above_character
            + self._collision_visuals
        )

    @override
    def event(self, e: PygameEvent) -> Scene:
        if (
            isinstance(e, KeyPressDown)
            and e.key is KeyboardKey.CONFIRM
            and (scene := self._npcs.trigger(self._player, self))
        ):
            return scene
        return replace(self, _player=self._player.event(e))

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        if self.next_event:
            return self.next_event

        player = self._player.tick(time_delta)
        logger.debug(t"Player {player.coordinate}")
        return self._move_to_scene(player) or replace(
            self, _player=self._player.tick(time_delta)
        )

    @cached_property
    def _foreground_and_characters(self) -> list[DrawOnScreen]:
        foregrounds = (
            LayerTileBottomAndDrawOnScreen(i, bottom, draw)
            for i, layer in enumerate(self._map_helper.foreground)
            for bottom, draw in layer
        )
        characters = chain([self._player], self._npcs.list)
        bottom_and_draw = sorted(
            map(self._map_helper.layer_bottom_and_draw, characters)
        )
        layers = merge(foregrounds, bottom_and_draw)
        return [draw for _, _, draw in layers]

    @cached_property
    @override
    def draw_on_screen_shift(self) -> Coordinate:
        player = self._player.draw_on_screen.rectangle.center
        map_width, map_height = self._map_helper.map_size
        gui_width, gui_height = gui_size()
        left_shift = _shift(player.left, gui_width, map_width)
        top_shift = _shift(player.top, gui_height, map_height)
        shift = Coordinate(left_shift, top_shift)
        logger.debug(t"Player shift {shift}")
        return shift

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


def _shift(player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
