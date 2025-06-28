"""
Map scene implementation.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from pathlib import Path
from typing import override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config import config
from nextrpg.core import Millisecond, Pixel
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen
from nextrpg.event.move import Move
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.model import Model, internal_field
from nextrpg.scene.map_helper import (
    MapHelper,
    TileBottomAndDraw,
    _LayerIndex,
    poly_from_obj,
)
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene


def _init_player(self: MapScene) -> CharacterOnScreen:
    player = self._map_helper.get_object(
        self.player_coordinate_object or config().map.player
    )
    speed = player.properties.get(
        config().map.properties.speed, config().character.speed
    )
    return CharacterOnScreen(
        self.initial_player_drawing,
        Coordinate(player.x, player.y),
        speed,
        self._map_helper.collisions,
    )


class MapScene(Model, Scene):
    """
    A scene implementation that represents a game map loaded from Tiled TMX.

    Handles rendering of map layers, character movement with collisions,
    and proper depth sorting of foreground elements relative to the player.

    Args:
        `tmx_file`: Path to the Tiled TMX file to load.

        `player_drawing`: Character drawing representing the player.
    """

    tmx_file: Path
    initial_player_drawing: CharacterDrawing
    player_coordinate_object: str | None = None
    moves: list[Move] = field(default_factory=list)
    _: KW_ONLY = field()
    _map_helper: MapHelper = internal_field(
        lambda self: MapHelper(self.tmx_file)
    )
    _player: CharacterOnScreen = internal_field(_init_player)

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
        draws = (
            self._map_helper.background
            + self._player.character_and_visuals.below_character_visuals
            + self._foreground_and_character
            + self._map_helper.above_character
            + self._player.character_and_visuals.above_character_visuals
        )
        return [d + self._player_offset for d in draws]

    @override
    def event(self, event: PygameEvent) -> Scene:
        """
        Process input events for the map scene.

        Delegates event handling to the player character and returns an
        updated scene with the new player state.

        Args:
            `event`: The pygame event to process.

        Returns:
            `Scene`: The updated scene after processing the event.
        """
        return replace(self, _player=self._player.event(event))

    @override
    def step(self, time_delta: Millisecond) -> Scene:
        """
        Update the map scene state for a single game step/frame.

        Updates the player character's position and animation state based on the
        elapsed time since the last frame.

        Args:
            `time_delta`: The time that has passed since the last update.

        Returns:
            `Scene`: The updated scene after the time step.
        """
        player = self._player.step(time_delta)
        return self._move_to_scene(player) or replace(self, _player=player)

    @property
    def _foreground_and_character(self) -> list[DrawOnScreen]:
        foregrounds = self._map_helper.foreground
        character = self._player.character_and_visuals.character
        player = TileBottomAndDraw(
            character.visible_rectangle.bottom, character
        )
        with_character = sorted(
            foregrounds[self._player_layer] | {player}, key=lambda t: t.bottom
        )
        layers = (
            foregrounds[: self._player_layer]
            + [with_character]
            + foregrounds[self._player_layer + 1 :]
        )
        return [draw for layer in layers for _, draw in layer]

    @property
    def _player_layer(self) -> _LayerIndex:
        reversed_layers = reversed(list(enumerate(self._map_helper.foreground)))
        return next(
            (i for i, layer in reversed_layers if self._above_player(layer)), 0
        )

    def _above_player(self, layer: set[TileBottomAndDraw]) -> bool:
        player = self._player.character_and_visuals.character.visible_rectangle
        return any(
            player.collide(draw.visible_rectangle) and bottom < player.bottom
            for bottom, draw in layer
        )

    @property
    def _player_offset(self) -> Coordinate:
        player = self._player.character_and_visuals.character.rectangle.center
        gui_width, gui_height = config().gui.size.tuple
        map_width, map_height = self._map_helper.map_size.tuple
        left_offset = _offset(player.left, gui_width, map_width)
        top_offset = _offset(player.top, gui_height, map_height)
        return Coordinate(left_offset, top_offset)

    def _move_to_scene(self, player: CharacterOnScreen) -> Scene | None:
        player_rect = player.character_and_visuals.character.visible_rectangle
        for move in self.moves:
            move_object = self._map_helper.get_object(move.trigger_object)
            move_area = poly_from_obj(move_object)
            if player_rect.collide(move_area):
                next_scene = move.to_scene(player.character)
                return TransitionScene(self, next_scene)
        return None


def _offset(player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
