"""
Map scene implementation.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import NamedTuple, override

from pygame import Surface
from pytmx import (
    TiledMap,
    TiledObject,
    TiledObjectGroup,
    TiledTileLayer,
    load_pygame,
)

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config import config
from nextrpg.core import Millisecond, Pixel
from nextrpg.draw_on_screen import (
    Coordinate,
    DrawOnScreen,
    Drawing,
    Rectangle,
    Size,
)
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.gui import Gui
from nextrpg.model import (
    initialize_internal_field,
    internal_field,
    is_internal_field_initialized,
)
from nextrpg.scene.scene import Scene

type _LayerIndex = int
type _Gid = int


@dataclass(frozen=True)
class _TiledCoordinate:
    top: int
    left: int


class _BottomAndDraw(NamedTuple):
    bottom: Pixel
    draw: DrawOnScreen


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
    _map_size: Size = internal_field()
    _background: list[DrawOnScreen] = internal_field()
    _foreground: list[set[_BottomAndDraw]] = internal_field()
    _player: CharacterOnScreen = internal_field()
    _above_character: list[DrawOnScreen] = internal_field()

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
            self._background
            + self._player.character_and_visuals.below_character_visuals
            + self._foreground_and_character
            + self._above_character
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
        if is_internal_field_initialized(self._map_size):
            return
        tmx = load_pygame(str(self.tmx_file))
        tile_size = Size(tmx.tilewidth, tmx.tileheight)
        initialize_internal_field(
            self,
            "_map_size",
            lambda: Size(
                tmx.width * tile_size.width, tmx.height * tile_size.height
            ),
        )
        initialize_internal_field(
            self,
            "_background",
            _draw_layers,
            tmx,
            tile_size,
            config().map.background,
        )
        initialize_internal_field(
            self, "_player", _player, tmx, self.character_drawing
        )
        initialize_internal_field(
            self,
            "_above_character",
            _draw_layers,
            tmx,
            tile_size,
            config().map.above_character,
        )
        gid_to_class = {
            tile["id"]: cls
            for tile in tmx.tile_properties.values()
            if (cls := tile.get("type"))
        }
        initialize_internal_field(
            self,
            "_foreground",
            lambda: [
                _bottom_and_draw(tmx, layer, tile_size, gid_to_class)
                for layer in _layers(tmx, config().map.foreground)
            ],
        )

    @cached_property
    def _foreground_and_character(self) -> list[DrawOnScreen]:
        foregrounds = [
            (layer_index, bottommost, draw)
            for layer_index, layer in enumerate(self._foreground)
            for bottommost, draw in layer
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
        reversed_layers = reversed(list(enumerate(self._foreground)))
        return next(
            (i for i, layer in reversed_layers if self._above_player(layer)), 0
        )

    def _above_player(self, layer: set[_BottomAndDraw]) -> bool:
        player = self._player.character_and_visuals.character.visible_rectangle
        return any(
            player.collide(draw.visible_rectangle) and bottom < player.bottom
            for bottom, draw in layer
        )

    @cached_property
    def _player_offset(self) -> Coordinate:
        player = self._player.character_and_visuals.character.rectangle.center
        gui_size = Gui.current_size()
        left_offset = _offset(player.left, gui_size.width, self._map_size.width)
        top_offset = _offset(player.top, gui_size.height, self._map_size.height)
        return Coordinate(left_offset, top_offset)


def _draw(
    layer: TiledTileLayer, tile_size: Size
) -> list[tuple[_TiledCoordinate, DrawOnScreen]]:
    return [
        (_TiledCoordinate(left, top), _tile(left, top, surface, tile_size))
        for left, top, surface in layer.tiles()
    ]


def _tile(
    left: int, top: int, surface: Surface, tile_size: Size
) -> DrawOnScreen:
    return DrawOnScreen(
        Coordinate(left * tile_size.width, top * tile_size.height),
        Drawing(surface),
    )


def _bottom_and_draw(
    tmx: TiledMap,
    layer: TiledTileLayer,
    tile_size: Size,
    gid_to_class: dict[_Gid, str],
) -> set[_BottomAndDraw]:
    coord_and_draws = _draw(layer, tile_size)
    gid_to_bottom = [
        (gid, draw.visible_rectangle.bottom)
        for coord, draw in coord_and_draws
        if (gid := _gid(tmx, layer, coord))
    ]
    return {
        _BottomAndDraw(
            _bottom(tmx, layer, coord, draw, gid_to_class, gid_to_bottom), draw
        )
        for coord, draw in coord_and_draws
    }


def _bottom(
    tmx: TiledMap,
    layer: TiledTileLayer,
    coord: _TiledCoordinate,
    draw: DrawOnScreen,
    gid_to_class: dict[_Gid, str],
    gid_to_bottom: list[tuple[_Gid, Pixel]],
) -> Pixel:
    if (gid := _gid(tmx, layer, coord)) and (cls := gid_to_class.get(gid)):
        return max(
            bottom for g, bottom in gid_to_bottom if gid_to_class[g] == cls
        )
    return draw.visible_rectangle.bottom


def _gid(
    tmx: TiledMap, layer: TiledTileLayer, coord: _TiledCoordinate
) -> _Gid | None:
    data_id = layer.data[coord.left][coord.top]
    return tmx.tile_properties.get(data_id, {}).get("id")


def _layers(
    tmx: TiledMap, name: str
) -> list[TiledTileLayer | TiledObjectGroup]:
    return [layer for layer in tmx.layers if layer.name.startswith(name)]


def _object(tmx: TiledMap, object_name: str) -> TiledObject:
    return next(
        obj
        for layer in _layers(tmx, config().map.object)
        for obj in layer
        if obj.name == object_name
    )


def _player(
    tmx: TiledMap, character_drawing: CharacterDrawing
) -> CharacterOnScreen:
    player = _object(tmx, config().map.player)
    return CharacterOnScreen(
        character_drawing,
        Coordinate(player.x, player.y),
        speed=player.properties.get(
            config().map.properties.speed, config().character.speed
        ),
        collisions=[
            Rectangle(Coordinate(rect.x, rect.y), Size(rect.width, rect.height))
            for layer in _layers(tmx, config().map.collision)
            for rect in layer
        ],
    )


def _draw_layers(
    tmx: TiledMap, tile_size: Size, name: str
) -> list[DrawOnScreen]:
    return [
        draw
        for layer in _layers(tmx, name)
        for _, draw in _draw(layer, tile_size)
    ]


def _offset(player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
