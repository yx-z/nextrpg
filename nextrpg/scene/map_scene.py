"""
Map scene implementation.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config import config
from nextrpg.core import Millisecond, Pixel
from nextrpg.draw_on_screen import (
    Coordinate,
    DrawOnScreen,
)
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.gui import Gui
from nextrpg.model import (
    init_internal_field,
    internal_field,
)
from nextrpg.scene.map_helper import MapHelper, TileBottomAndDraw
from nextrpg.scene.scene import Scene

type _LayerIndex = int


@dataclass(frozen=True)
class MapScene(Scene):
    """
    A scene implementation that represents a game map loaded from Tiled TMX.

    Handles rendering of map layers, character movement with collisions,
    and proper depth sorting of foreground elements relative to the player.

    Args:
        `tmx_file`: Path to the Tiled TMX file to load.

        `character_drawing`: Character drawing representing the player.
    """

    tmx_file: Path
    character_drawing: CharacterDrawing
    _: KW_ONLY = internal_field()
    _map_helper: MapHelper = internal_field()
    _player: CharacterOnScreen = internal_field()

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
        return replace(self, _player=self._player.step(time_delta))

    def __post_init__(self) -> None:
        init_internal_field(self, "_map_helper", MapHelper, self.tmx_file)
        init_internal_field(self, "_player", self._init_player)

    @cached_property
    def _foreground_and_character(self) -> list[DrawOnScreen]:
        foregrounds = [
            (i, bottom, draw)
            for i, layer in enumerate(self._map_helper.foreground)
            for bottom, draw in layer
        ]
        character = self._player.character_and_visuals.character
        player = (
            self._player_layer,
            character.visible_rectangle.bottom,
            character,
        )
        sort_by_layer_index_and_bottommost = sorted(
            foregrounds + [player], key=lambda t: t[:2]
        )
        return [draw for _, _, draw in sort_by_layer_index_and_bottommost]

    @cached_property
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

    @cached_property
    def _player_offset(self) -> Coordinate:
        player = self._player.character_and_visuals.character.rectangle.center
        gui_width, gui_height = Gui.current_size().tuple
        map_width, map_height = self._map_helper.map_size.tuple
        left_offset = _offset(player.left, gui_width, map_width)
        top_offset = _offset(player.top, gui_height, map_height)
        return Coordinate(left_offset, top_offset)

    def _init_player(self) -> CharacterOnScreen:
        player = self._map_helper.get_object(config().map.player)
        speed = player.properties.get(
            config().map.properties.speed, config().character.speed
        )
        collisions = []
        return CharacterOnScreen(
            self.character_drawing,
            Coordinate(player.x, player.y),
            speed,
            collisions,
        )


def _offset(player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
