from dataclasses import dataclass, field
from functools import cached_property, lru_cache
from pathlib import Path
from typing import NamedTuple

from pygame import Surface
from pytmx import (
    TiledMap,
    TiledObject,
    TiledObjectGroup,
    TiledTileLayer,
    load_pygame,
)

from nextrpg.config import config
from nextrpg.core import Coordinate, Pixel, Size
from nextrpg.draw_on_screen import DrawOnScreen, Drawing

type _Gid = int


@dataclass(frozen=True)
class _TiledCoordinate:
    top: int
    left: int


class TileBottomAndDraw(NamedTuple):
    """
    Represents a foreground tile of the bottommost pixel from its tile class,
    and a `DrawOnScreen` of the tile itself.

    This is particularly useful for foreground tiles when performing y-sorting
    to determine the laying between the character and the tile: bigger y-axis
    (closer to the bottom) means closer to the camera and hence obstructing
    tiles/characters above it.

    We need to group the tiles given a single graphical object may be split
    into multiple tiles in a Tiled tmx map.

    Attributes:
        `bottom`: The bottommost pixel for the tile group that this tile is in.

        `draw`: The `DrawOnScreen` of the tile itself.
    """

    bottom: Pixel
    draw: DrawOnScreen


@dataclass(frozen=True)
class MapHelper:
    """
    Tiled tmx map helper class for loading the tiles.

    Attributes:
        `tmx_file`: Tmx file path to load.
    """

    tmx_file: Path
    tmx: TiledMap = field(init=False)

    @cached_property
    def map_size(self) -> Size:
        """
        Return the full map size in pixels.

        Returns:
            `Size`: The map size.
        """
        tile_width, tile_height = self._tile_size.tuple
        return Size(self.tmx.width * tile_width, self.tmx.height * tile_height)

    @cached_property
    def background(self) -> list[DrawOnScreen]:
        """
        The list of background drawings.

        Returns:
            `list[DrawOnScreen]`: The list of background drawings.
        """
        return self._draw_layers(config().map.background)

    @cached_property
    def foreground(self) -> list[set[TileBottomAndDraw]]:
        """
        The list of foreground drawings with bottom pixel info.
        The list is in increasing order of layer index, meaning the layer
        shall obstruct previous tiles.

        Returns:
            `list[set[TileBottomAndDraw]]`: The list of foreground drawings.
        """
        return [
            self._bottom_and_draw(layer)
            for layer in self.get_layers(config().map.foreground)
        ]

    @cached_property
    def above_character(self) -> list[DrawOnScreen]:
        """
        The list of above-character drawings.

        Returns:
            `list[DrawOnScreen]`: The list of above-character drawings.
        """
        return self._draw_layers(config().map.above_character)

    @lru_cache
    def get_object(self, name: str) -> TiledObject:
        """
        Get the object of the given name from object layers.

        Arguments:
            `name`: The unique name to retrieve the object by.

        Returns:
            `TiledObject`: The tile object with the given name.
        """
        return next(
            obj
            for layer in self.get_layers(config().map.object)
            for obj in layer
            if obj.name == name
        )

    @lru_cache
    def get_layers(
        self, prefix: str
    ) -> list[TiledTileLayer | TiledObjectGroup]:
        """
        Retrieve layers with the given prefix from the map.

        Arguments:
            `prefix`: The prefix of the layer name to retrieve.

        Returns:
            `list[TiledTileLayer | TiledObjectGroup]`: The matched layers.
        """
        return [
            layer for layer in self.tmx.layers if layer.name.startswith(prefix)
        ]

    def _draw_layers(self, name: str) -> list[DrawOnScreen]:
        return [
            draw
            for layer in self.get_layers(name)
            for _, draw in self._draw(layer)
        ]

    def _bottom_and_draw(self, layer: TiledTileLayer) -> set[TileBottomAndDraw]:
        coord_and_draws = self._draw(layer)
        gid_to_bottom = [
            (gid, draw.visible_rectangle.bottom)
            for coord, draw in coord_and_draws
            if (gid := self._gid(layer, coord))
        ]
        return {
            TileBottomAndDraw(
                self._bottom(layer, coord, draw, gid_to_bottom), draw
            )
            for coord, draw in coord_and_draws
        }

    @cached_property
    def _tile_size(self) -> Size:
        return Size(self.tmx.tilewidth, self.tmx.tileheight)

    def _draw(
        self, layer: TiledTileLayer
    ) -> list[tuple[_TiledCoordinate, DrawOnScreen]]:
        return [
            (_TiledCoordinate(top, left), self._tile(left, top, surface))
            for left, top, surface in layer.tiles()
        ]

    def _tile(self, left: int, top: int, surface: Surface) -> DrawOnScreen:
        width, height = self._tile_size.tuple
        return DrawOnScreen(
            Coordinate(left * width, top * height),
            Drawing(surface),
        )

    def _gid(
        self, layer: TiledTileLayer, coord: _TiledCoordinate
    ) -> _Gid | None:
        data_id = layer.data[coord.top][coord.left]
        return self.tmx.tile_properties.get(data_id, {}).get("id")

    def _bottom(
        self,
        layer: TiledTileLayer,
        coord: _TiledCoordinate,
        draw: DrawOnScreen,
        gid_to_bottom: list[tuple[_Gid, Pixel]],
    ) -> Pixel:
        if (gid := self._gid(layer, coord)) and (
            cls := self._gid_to_class.get(gid)
        ):
            return max(
                bottom
                for g, bottom in gid_to_bottom
                if self._gid_to_class[g] == cls
            )
        return draw.visible_rectangle.bottom

    @cached_property
    def _gid_to_class(self) -> dict[_Gid, str]:
        return {
            tile["id"]: cls
            for tile in self.tmx.tile_properties.values()
            if (cls := tile.get("type"))
        }

    def __post_init__(self) -> None:
        object.__setattr__(self, "tmx", load_pygame(str(self.tmx_file)))
