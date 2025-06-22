"""
Map scene implementation.
"""

from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from itertools import groupby
from pathlib import Path
from typing import NamedTuple, override

from pygame import Surface
from pytmx import (
    TiledMap,
    TiledObjectGroup,
    TiledTileLayer,
    load_pygame,
)

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config import config
from nextrpg.core import (
    INTERNAL,
    Millisecond,
    Pixel,
    initialize_internal_field,
    is_internal_field_initialized,
)
from nextrpg.draw_on_screen import (
    Coordinate,
    DrawOnScreen,
    Drawing,
    Rectangle,
    Size,
)
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.gui import Gui
from nextrpg.scene.scene import Scene

type _LayerIndex = int


class _TiledCoordinate(NamedTuple):
    top: int
    left: int


type _Gid = int | _TiledCoordinate


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
    _: KW_ONLY = INTERNAL
    _map_size: Size = INTERNAL
    _background: list[DrawOnScreen] = INTERNAL
    _foreground: list[dict[_Gid, DrawOnScreen]] = INTERNAL
    _player: CharacterOnScreen = INTERNAL
    _above_character: list[DrawOnScreen] = INTERNAL
    _gid_groups: dict[_Gid, set[DrawOnScreen]] = INTERNAL

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
            self, "_player", _player, self.character_drawing, tmx
        )
        initialize_internal_field(
            self,
            "_above_character",
            _draw_layers,
            tmx,
            tile_size,
            config().map.above_character,
        )
        foreground = [
            _get_gid_and_draw(tmx, layer, tile_size)
            for layer in _layers(tmx, config().map.foreground)
        ]
        initialize_internal_field(self, "_foreground", lambda: foreground)
        gids = {
            gid: draw for layer in foreground for gid, draw in layer.items()
        }
        initialize_internal_field(self, "_gid_groups", _gid_groups, tmx, gids)

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
            + self._player.draw_on_screen.below_character_visuals
            + self._foreground_and_character
            + self._above_character
            + self._player.draw_on_screen.above_character_visuals
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

    @cached_property
    def _foreground_and_character(self) -> list[DrawOnScreen]:
        sorted_by_layer_index_and_bottom = sorted(
            self._layer_gid_draws,
            key=lambda t: _LayerIndexAndBottom(
                t[0], _max_bottom(self._grouped_rectangles(*t[1:]))
            ),
        )
        return [draw for _, _, draw in sorted_by_layer_index_and_bottom]

    @cached_property
    def _layer_gid_draws(self) -> list[tuple[_LayerIndex, _Gid, DrawOnScreen]]:
        foregrounds = list(
            (layer_index, gid, draw)
            for layer_index, gid_to_draws in enumerate(self._foreground)
            for gid, draw in gid_to_draws.items()
        )
        player = (self._player_layer, 0, self._player.draw_on_screen.character)
        return foregrounds + [player]

    @cached_property
    def _player_layer(self) -> _LayerIndex:
        reversed_layers = reversed(list(enumerate(self._foreground)))
        return next(
            (i for i, layer in reversed_layers if self._below_player(layer)), 0
        )

    @cached_property
    def _player_offset(self) -> Coordinate:
        player = self._player.draw_on_screen.character.rectangle.center
        gui_size = Gui.current_size()
        left_offset = _offset(player.left, gui_size.width, self._map_size.width)
        top_offset = _offset(player.top, gui_size.height, self._map_size.height)
        return Coordinate(left_offset, top_offset)

    def _below_player(self, layer: dict[_Gid, DrawOnScreen]) -> bool:
        player = self._player.draw_on_screen.character.visible_rectangle
        return any(
            any(
                player.collide(rect) and rect.bottom < player.bottom
                for rect in self._grouped_rectangles(gid, draw)
            )
            for gid, draw in layer.items()
        )

    def _grouped_rectangles(
        self, gid: _Gid, draw: DrawOnScreen
    ) -> list[Rectangle]:
        return [
            d.visible_rectangle for d in (self._gid_groups.get(gid) or {draw})
        ]


def _max_bottom(rectangles: list[Rectangle]) -> Pixel:
    return max(rectangle.bottom for rectangle in rectangles)


def _draw(
    layer: TiledTileLayer, tile_size: Size
) -> dict[_TiledCoordinate, DrawOnScreen]:
    return {
        _TiledCoordinate(left, top): _tile(left, top, surface, tile_size)
        for left, top, surface in layer.tiles()
    }


def _tile(
    left: int, top: int, surface: Surface, tile_size: Size
) -> DrawOnScreen:
    return DrawOnScreen(
        Coordinate(left * tile_size.width, top * tile_size.height),
        Drawing(surface),
    )


def _get_gid_and_draw(
    tmx: TiledMap, layer: TiledTileLayer, tile_size: Size
) -> dict[_Gid, DrawOnScreen]:
    return {
        _gid(tmx, layer, coord): draw
        for coord, draw in _draw(layer, tile_size).items()
    }


def _gid(tmx: TiledMap, layer: TiledTileLayer, coord: _TiledCoordinate) -> _Gid:
    return tmx.tile_properties.get(layer.data[coord.left][coord.top], {}).get(
        "id", coord
    )


def _layers(
    tmx: TiledMap, name: str
) -> list[TiledTileLayer | TiledObjectGroup]:
    return [layer for layer in tmx.layers if layer.name.startswith(name)]


def _player(
    character_drawing: CharacterDrawing, tmx: TiledMap
) -> CharacterOnScreen:
    player = next(
        obj
        for layer in _layers(tmx, config().map.object)
        for obj in layer
        if obj.name == config().map.player
    )
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


def _gid_groups(
    tmx: TiledMap, draw_on_screens: dict[_Gid, DrawOnScreen]
) -> dict[_Gid, set[DrawOnScreen]]:
    gid_to_class = {
        tile["id"]: cls
        for tile in tmx.tile_properties.values()
        if (cls := tile.get("type"))
    }
    groups = (
        {gid: draw_on_screens.get(gid) for gid, _ in gid_group}
        for _, gid_group in groupby(
            sorted(gid_to_class.items(), key=lambda x: x[1]), key=lambda x: x[1]
        )
    )
    return {
        gid: set(draw for draw in gid_to_draw.values() if draw)
        for gid_to_draw in groups
        for gid in gid_to_draw
    }


def _draw_layers(
    tmx: TiledMap, tile_size: Size, name: str
) -> list[DrawOnScreen]:
    return [
        draw
        for layer in _layers(tmx, name)
        for _, draw in _draw(layer, tile_size).items()
    ]


class _LayerIndexAndBottom(NamedTuple):
    layer: _LayerIndex
    bottom: Pixel


def _offset(player_axis: Pixel, gui_axis: Pixel, map_axis: Pixel) -> Pixel:
    if player_axis < gui_axis / 2:
        return 0
    if player_axis > map_axis - gui_axis / 2:
        return gui_axis - map_axis
    return gui_axis / 2 - player_axis
