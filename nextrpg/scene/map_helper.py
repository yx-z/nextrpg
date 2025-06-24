from dataclasses import KW_ONLY, field
from functools import cached_property, lru_cache
from itertools import product
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
from nextrpg.core import Pixel, Size
from nextrpg.draw_on_screen import (
    Coordinate,
    DrawOnScreen,
    Drawing,
    Polygon,
    Rectangle,
)
from nextrpg.model import Model, internal_field


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


type _Gid = int
type _LayerIndex = int


class _TiledCoordinate(NamedTuple):
    top: int
    left: int


class _Collider(NamedTuple):
    coord: _TiledCoordinate
    obj: TiledObject


class MapHelper(Model):
    """
    Tiled tmx map helper class for loading the tiles.

    Attributes:
        `tmx_file`: Tmx file path to load.
    """

    tmx_file: Path
    _: KW_ONLY = field()
    _tmx: TiledMap = internal_field(
        lambda self: load_pygame(str(self.tmx_file))
    )

    @cached_property
    def map_size(self) -> Size:
        """
        Return the full map size in pixels.

        Returns:
            `Size`: The map size.
        """
        tile_width, tile_height = self._tile_size.tuple
        return Size(
            self._tmx.width * tile_width, self._tmx.height * tile_height
        )

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
            for layer in self._tile_layers(config().map.foreground)
        ]

    @cached_property
    def above_character(self) -> list[DrawOnScreen]:
        """
        The list of above-character drawings.

        Returns:
            `list[DrawOnScreen]`: The list of above-character drawings.
        """
        return self._draw_layers(config().map.above_character)

    @cached_property
    def collisions(self) -> list[Polygon]:
        """
        Retrieve collision polygons from the tiles.

        Returns:
            `list[Polygon]`: List of collision polygons.
        """
        return [
            polygon
            for coord, obj in self._colliders
            if (polygon := self._polygon(coord, obj))
        ]

    @lru_cache
    def get_object(self, name: str) -> TiledObject:
        """
        Get the first object of the given name from ALL object layers.

        Arguments:
            `name`: The unique name to retrieve the object by.

        Returns:
            `TiledObject`: The tile object with the given name.
        """
        return self.get_objects(name)[0]

    @lru_cache
    def get_objects(self, name: str) -> list[TiledObject]:
        """
        Get ALL objects of the given name from ALL object layers.

        Arguments:
            `name`: The unique name to retrieve the object by.

        Returns:
            `list[TiledObject]`: The tile objects with the given name.
        """
        return [
            obj
            for layer in map(self._layer, self._tmx.visible_object_groups)
            for obj in layer
            if obj.name == name
        ]

    @cached_property
    def _colliders(self) -> list[_Collider]:
        return [
            _Collider(_TiledCoordinate(x, y), c)
            for layer in self._all_tile_layers
            for x, y, gid in layer
            if (c := self._collider(gid))
        ]

    def _collider(self, gid: _Gid) -> TiledObject | None:
        colliders = self._tmx.tile_properties.get(gid, {}).get("colliders")
        return colliders[0] if colliders else None

    def _polygon(
        self, coord: _TiledCoordinate, obj: TiledObject
    ) -> Polygon | None:
        return self._from_points(coord, obj) or self._from_rect(coord, obj)

    def _from_points(
        self, coord: _TiledCoordinate, obj: TiledObject
    ) -> Polygon | None:
        if not (points := getattr(obj, "points", None)):
            return None
        w, h = self._tile_size.tuple
        cx, cy = coord
        return Polygon([Coordinate(cx * w + x, cy * h + y) for x, y in points])

    def _from_rect(
        self, coord: _TiledCoordinate, obj: TiledObject
    ) -> Rectangle | None:
        if not all(hasattr(obj, attr) for attr in _RECT_ATTRS):
            return None
        w, h = self._tile_size.tuple
        cx, cy = coord
        return Rectangle(
            Coordinate(cx * w + obj.x, cy * h + obj.y),
            Size(obj.width, obj.height),
        )

    def _tile_layers(self, class_name: str) -> list[TiledTileLayer]:
        return [
            layer
            for layer in self._all_tile_layers
            if getattr(layer, "class", None) == class_name
        ]

    @cached_property
    def _all_tile_layers(self) -> list[TiledTileLayer]:
        return list(map(self._layer, self._tmx.visible_tile_layers))

    def _draw_layers(self, class_name: str) -> list[DrawOnScreen]:
        return [
            draw
            for layer in self._tile_layers(class_name)
            for _, draw in self._draw(layer)
        ]

    def _bottom_and_draw(self, layer: TiledTileLayer) -> set[TileBottomAndDraw]:
        coord_and_draws = self._draw(layer)
        gid_coord_and_bottom = [
            (gid, coord, draw.visible_rectangle.bottom)
            for coord, draw in coord_and_draws
            if (gid := self._gid(layer, coord))
        ]
        return {
            TileBottomAndDraw(
                self._bottom(layer, coord, draw, gid_coord_and_bottom), draw
            )
            for coord, draw in coord_and_draws
        }

    @cached_property
    def _tile_size(self) -> Size:
        return Size(self._tmx.tilewidth, self._tmx.tileheight)

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
        return self._tmx.tile_properties.get(data_id, {}).get("id")

    def _bottom(
        self,
        layer: TiledTileLayer,
        coord: _TiledCoordinate,
        draw: DrawOnScreen,
        gid_coord_and_bottom: list[tuple[_Gid, _TiledCoordinate, Pixel]],
    ) -> Pixel:
        if (gid := self._gid(layer, coord)) and (
            cls := self._gid_to_class.get(gid)
        ):
            return max(
                bottom
                for g, c, bottom in gid_coord_and_bottom
                if self._gid_to_class[g] == cls and c in _neighbors(coord)
            )
        return draw.visible_rectangle.bottom

    @cached_property
    def _gid_to_class(self) -> dict[_Gid, str]:
        return {
            tile["id"]: cls
            for tile in self._tmx.tile_properties.values()
            if (cls := tile.get("type"))
        }

    def _layer(self, index: _LayerIndex) -> TiledTileLayer | TiledObjectGroup:
        return self._tmx.layers[index]


def _neighbors(coord: _TiledCoordinate) -> set[_TiledCoordinate]:
    deltas = {-1, 0, 1}
    x, y = coord
    return {
        _TiledCoordinate(x + dx, y + dy) for dx, dy in product(deltas, deltas)
    }


_RECT_ATTRS = {"x", "y", "width", "height"}
