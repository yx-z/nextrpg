from dataclasses import KW_ONLY, field
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
from nextrpg.core import Pixel, Size
from nextrpg.draw_on_screen import (
    Coordinate,
    DrawOnScreen,
    Drawing,
    GenericPolygon,
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


class _TileCoordinate(NamedTuple):
    top: int
    left: int


class _Collider(NamedTuple):
    coord: _TileCoordinate
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

        The background layers are ones marked with the class name
        `config().map.background`.

        Returns:
            `list[DrawOnScreen]`: The list of background drawings.
        """
        return self._draw_layers(config().map.background)

    @cached_property
    def foreground(self) -> list[set[TileBottomAndDraw]]:
        """
        The list of foreground drawings with bottom pixel info.

        The foreground layers are ones marked with the class name
        `config().map.foreground`.

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
        Get the list of above-character drawings, which are all layers
        with the class name `config().map.above_character`.

        Returns:
            `list[DrawOnScreen]`: The list of above-character drawings.
        """
        return self._draw_layers(config().map.above_character)

    @cached_property
    def collisions(self) -> list[Polygon]:
        """
        Retrieve collision polygons from the tiles and objects.
        1. From tiles: mark the tile collision polygon/rectangle in tileset.
        2. From objects: mark the polygon/rectangle object class as
            `config().map.collision`.

        Returns:
            `list[Polygon]`: List of collision polygons.
        """
        from_tiles = [
            self._polygon(coord, obj) for coord, obj in self._colliders
        ]
        from_objects: list[Polygon] = [
            GenericPolygon([Coordinate(x, y) for x, y in obj.as_points])
            for obj in self.get_objects_by_class_name(config().map.collision)
        ]
        return from_tiles + from_objects

    @lru_cache
    def get_object(self, name: str) -> TiledObject:
        """
        Get the first object of the given name from all visible object layers.

        Arguments:
            `name`: The unique name to retrieve the object by.

        Returns:
            `TiledObject`: The tile object with the given name.
        """
        return next(obj for obj in self._all_objects if obj.name == name)

    @lru_cache
    def get_objects_by_class_name(self, class_name: str) -> list[TiledObject]:
        """
        Get objects of the given class name from all visible object layers.

        Arguments:
            `class_name`: The class name to retrieve objects by.

        Returns:
            `list[TiledObject]`: The tile objects with the given name.
        """
        return [obj for obj in self._all_objects if obj.type == class_name]

    @cached_property
    def _all_objects(self) -> list[TiledObject]:
        return [
            obj
            for layer in map(self._layer, self._tmx.visible_object_groups)
            for obj in layer
        ]

    @cached_property
    def _colliders(self) -> list[_Collider]:
        return [
            _Collider(_TileCoordinate(x, y), c)
            for layer in self._all_tile_layers
            for x, y, gid in layer
            if (c := self._collider(gid))
        ]

    def _collider(self, gid: _Gid) -> TiledObject | None:
        colliders = self._tmx.tile_properties.get(gid, {}).get("colliders")
        return colliders[0] if colliders else None

    def _polygon(self, coord: _TileCoordinate, obj: TiledObject) -> Polygon:
        return self._from_rect(coord, obj) or self._from_points(coord, obj)

    def _from_points(
        self, coord: _TileCoordinate, obj: TiledObject
    ) -> GenericPolygon:
        w, h = self._tile_size.tuple
        cx, cy = coord
        return GenericPolygon(
            [Coordinate(cx * w + x, cy * h + y) for x, y in obj.as_points]
        )

    def _from_rect(
        self, coord: _TileCoordinate, obj: TiledObject
    ) -> Rectangle | None:
        if (
            obj.x is None
            or obj.y is None
            or obj.width is None
            or obj.height is None
        ):
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
            for draw in self._draw(layer).values()
        ]

    def _bottom_and_draw(self, layer: TiledTileLayer) -> set[TileBottomAndDraw]:
        coord_and_draws = self._draw(layer)
        coord_to_bottom = {
            coord: draw.visible_rectangle.bottom
            for coord, draw in coord_and_draws.items()
        }
        return {
            TileBottomAndDraw(
                self._bottom(layer, coord, draw, coord_to_bottom), draw
            )
            for coord, draw in coord_and_draws.items()
        }

    @cached_property
    def _tile_size(self) -> Size:
        return Size(self._tmx.tilewidth, self._tmx.tileheight)

    def _draw(
        self, layer: TiledTileLayer
    ) -> dict[_TileCoordinate, DrawOnScreen]:
        return {
            _TileCoordinate(top, left): self._tile(left, top, surface)
            for left, top, surface in layer.tiles()
        }

    def _tile(self, left: int, top: int, surface: Surface) -> DrawOnScreen:
        width, height = self._tile_size.tuple
        return DrawOnScreen(
            Coordinate(left * width, top * height),
            Drawing(surface),
        )

    def _class(
        self, layer: TiledTileLayer, coord: _TileCoordinate
    ) -> str | None:
        x, y = coord
        if 0 <= x < len(layer.data) and 0 <= y < len(layer.data[x]):
            data_id = layer.data[x][y]
            return self._gid_to_cls.get(
                self._tmx.tile_properties.get(data_id, {}).get("id")
            )
        return None

    def _bottom(
        self,
        layer: TiledTileLayer,
        coord: _TileCoordinate,
        draw: DrawOnScreen,
        coord_to_bottom: dict[_TileCoordinate, Pixel],
    ) -> Pixel:
        if cls := self._class(layer, coord):
            return max(
                coord_to_bottom[c] for c in self._component(layer, coord, cls)
            )
        return draw.visible_rectangle.bottom

    def _component(
        self,
        layer: TiledTileLayer,
        coord: _TileCoordinate,
        cls: str,
        visited: set[_TileCoordinate] | None = None,
    ) -> set[_TileCoordinate]:
        visited = (visited or set()) | {coord}
        return visited | {
            c
            for neighbor in self._neighbors(layer, coord, cls) - visited
            for c in self._component(layer, neighbor, cls, visited)
        }

    def _neighbors(
        self, layer: TiledTileLayer, coord: _TileCoordinate, cls: str
    ) -> set[_TileCoordinate]:
        x, y = coord
        return {
            c
            for dx, dy in {(0, 1), (1, 0), (0, -1), (-1, 0)}
            if self._class(layer, c := _TileCoordinate(x + dx, y + dy)) == cls
        }

    @cached_property
    def _gid_to_cls(self) -> dict[_Gid, str]:
        return {
            tile["id"]: cls
            for tile in self._tmx.tile_properties.values()
            if (cls := tile.get("type"))
        }

    def _layer(self, index: _LayerIndex) -> TiledTileLayer | TiledObjectGroup:
        return self._tmx.layers[index]
