from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from os import PathLike
from typing import NamedTuple

from pygame import Surface
from pytmx import (
    TiledMap,
    TiledObject,
    TiledObjectGroup,
    TiledTileLayer,
    load_pygame,
)

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.cached_decorator import cached
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Height, Size
from nextrpg.core.log import Log
from nextrpg.draw.draw import (
    Draw,
    DrawOnScreen,
    PolygonOnScreen,
    RectangleOnScreen,
)
from nextrpg.global_config.global_config import config

log = Log()


class TileBottomAndDrawOnScreen(NamedTuple):
    bottom: Height
    draw: DrawOnScreen


class LayerTileBottomAndDrawOnScreen(NamedTuple):
    layer: int
    bottom: Height
    draw_on_screen: DrawOnScreen


def get_polygon(obj: TiledObject) -> PolygonOnScreen | None:
    if hasattr(obj, "points"):
        return PolygonOnScreen(
            tuple(Coordinate(x, y) for x, y in obj.points), obj.closed
        )
    if _is_rect(obj):
        return RectangleOnScreen(
            Coordinate(obj.x, obj.y), Size(obj.width, obj.height)
        )
    return None


@cached(lambda: config().map.cache_size)
@dataclass(frozen=True)
class MapLoader:

    tmx_file: PathLike | str

    @cached_property
    def map_size(self) -> Size:
        tile_width, tile_height = self._tile_size
        width = self._tmx.width * tile_width
        height = self._tmx.height * tile_height
        return Size(width, height)

    @cached_property
    def background(self) -> tuple[DrawOnScreen, ...]:
        return self._draw_layers(config().map.background)

    @cached_property
    def foreground(
        self,
    ) -> tuple[tuple[LayerTileBottomAndDrawOnScreen, ...], ...]:
        return tuple(
            _foreground_layer(i, tiles)
            for i, layer in enumerate(
                self._tile_layers(config().map.foreground)
            )
            if (tiles := self._bottom_and_draw(layer))
        )

    @cached_property
    def above_character(self) -> tuple[DrawOnScreen, ...]:
        return self._draw_layers(config().map.above_character)

    @cached_property
    def collisions(self) -> tuple[PolygonOnScreen, ...]:
        from_tiles = tuple(
            self._polygon(coord, obj) for coord, obj in self._colliders
        )
        from_objects = tuple(
            poly
            for obj in self.get_objects_by_class_name(config().map.collision)
            if (poly := get_polygon(obj))
        )
        return from_tiles + from_objects

    @cached_property
    def collision_visuals(self) -> tuple[DrawOnScreen, ...]:
        if config().debug and (
            color := config().debug.collision_rectangle_color
        ):
            return tuple(c.fill(color) for c in self.collisions)
        return ()

    def get_object(self, name: str) -> TiledObject:
        for obj in self._all_objects:
            if obj.name == name:
                return obj
        raise RuntimeError(f"Object {name} not found.")

    def get_objects_by_class_name(
        self, class_name: str
    ) -> tuple[TiledObject, ...]:
        return tuple(obj for obj in self._all_objects if obj.type == class_name)

    def layer_bottom_and_draw(
        self, character: CharacterOnScreen
    ) -> tuple[LayerTileBottomAndDrawOnScreen, ...]:
        character_layer = self._character_layer(character)
        character_bottom = (
            character.draw_on_screen.visible_rectangle_on_screen.bottom
        )
        return tuple(
            LayerTileBottomAndDrawOnScreen(
                character_layer, character_bottom, draw_on_screen
            )
            for draw_on_screen in character.draw_on_screens
        )

    def _character_layer(self, character: CharacterOnScreen) -> int:
        for index, layer in enumerate(self._reversed_foregrounds):
            if _below_character_layer(layer, character):
                return index
        return 0

    @cached_property
    def _reversed_foregrounds(
        self,
    ) -> tuple[tuple[LayerTileBottomAndDrawOnScreen, ...], ...]:
        return tuple(reversed(self.foreground))

    @cached_property
    def _all_objects(self) -> tuple[TiledObject, ...]:
        return tuple(
            obj
            for i in self._tmx.visible_object_groups
            for obj in self._layer(i)
        )

    @cached_property
    def _colliders(self) -> tuple[_Collider, ...]:
        return tuple(
            _Collider(_TileCoordinate(x, y), collider)
            for layer in self._all_tile_layers
            for x, y, gid in layer
            for collider in self._collider(gid)
        )

    def _collider(self, gid: _Gid) -> tuple[TiledObject, ...]:
        return tuple(
            self._tmx.tile_properties.get(gid, {}).get("colliders", ())
        )

    def _polygon(
        self, coord: _TileCoordinate, obj: TiledObject
    ) -> PolygonOnScreen:
        return self._from_rect(coord, obj) or self._from_points(coord, obj)

    def _from_points(
        self, coord: _TileCoordinate, obj: TiledObject
    ) -> PolygonOnScreen:
        w, h = self._tile_size
        cx, cy = coord
        return PolygonOnScreen(
            tuple(Coordinate(cx * w + x, cy * h + y) for x, y in obj.as_points)
        )

    def _from_rect(
        self, coord: _TileCoordinate, obj: TiledObject
    ) -> RectangleOnScreen | None:
        if not _is_rect(obj):
            return None

        w, h = self._tile_size
        cx, cy = coord
        map_coord = Coordinate(cx * w + obj.x, cy * h + obj.y)
        size = Size(obj.width, obj.height)
        return RectangleOnScreen(map_coord, size)

    def _tile_layers(self, class_name: str) -> tuple[TiledTileLayer, ...]:
        return tuple(
            layer
            for layer in self._all_tile_layers
            if getattr(layer, "class", None) == class_name
        )

    @cached_property
    def _all_tile_layers(self) -> tuple[TiledTileLayer, ...]:
        return tuple(self._layer(i) for i in self._tmx.visible_tile_layers)

    def _draw_layers(self, class_name: str) -> tuple[DrawOnScreen, ...]:
        return tuple(
            draw
            for layer in self._tile_layers(class_name)
            for draw in self._draw(layer).values()
        )

    def _bottom_and_draw(
        self, layer: TiledTileLayer
    ) -> tuple[TileBottomAndDrawOnScreen, ...]:
        coord_and_draws = self._draw(layer)
        coord_to_bottom = {
            coord: draw.visible_rectangle_on_screen.bottom
            for coord, draw in coord_and_draws.items()
        }
        bottom_and_draw = tuple(
            TileBottomAndDrawOnScreen(
                self._bottom(layer, coord, draw, coord_to_bottom), draw
            )
            for coord, draw in coord_and_draws.items()
        )
        return tuple(sorted(bottom_and_draw, key=lambda t: t.bottom))

    @property
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
        width, height = self._tile_size
        return DrawOnScreen(
            Coordinate(left * width, top * height),
            Draw(surface),
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
        coord_to_bottom: dict[_TileCoordinate, Height],
    ) -> Height:
        return (
            max(coord_to_bottom[c] for c in self._component(layer, coord, cls))
            if (cls := self._class(layer, coord))
            else draw.visible_rectangle_on_screen.bottom
        )

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
            for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0))
            if self._class(layer, c := _TileCoordinate(x + dx, y + dy)) == cls
        }

    @cached_property
    def _gid_to_cls(self) -> dict[_Gid, str]:
        return {
            tile["id"]: cls
            for tile in self._tmx.tile_properties.values()
            if (cls := tile.get("type"))
        }

    def _layer(self, index: int) -> TiledTileLayer | TiledObjectGroup:
        return self._tmx.layers[index]

    @cached_property
    def _tmx(self) -> TiledMap:
        log.debug(t"Loading {self.tmx_file}")
        return load_pygame(str(self.tmx_file))


def _below_character_layer(
    layer: tuple[LayerTileBottomAndDrawOnScreen, ...],
    character: CharacterOnScreen,
) -> bool:
    rect = character.draw_on_screen.visible_rectangle_on_screen
    return layer[-1].bottom < rect.bottom and any(
        bottom < rect.bottom and rect.collide(draw.visible_rectangle_on_screen)
        for _, bottom, draw in layer
    )


def _is_rect(obj: TiledObject) -> bool:
    return obj.x is not None and obj.y is not None and obj.width and obj.height


def _foreground_layer(
    idx: int, tiles: tuple[TileBottomAndDrawOnScreen, ...]
) -> tuple[LayerTileBottomAndDrawOnScreen, ...]:
    return tuple(
        LayerTileBottomAndDrawOnScreen(idx, bottom, draw)
        for bottom, draw in tiles
    )


type _Gid = int


class _TileCoordinate(NamedTuple):
    top: int
    left: int


class _Collider(NamedTuple):
    coord: _TileCoordinate
    obj: TiledObject
