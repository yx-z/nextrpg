from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import NamedTuple, Self

from pytmx import TiledObject, TiledTileLayer

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.animation.cyclic_animation_on_screen import CyclicAnimationOnScreen
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.log import Log
from nextrpg.core.time import Millisecond
from nextrpg.core.tmx_loader import TmxLoader, get_geometry, is_rect
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate, YAxis
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.polygon_area_on_screen import PolygonAreaOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

log = Log()


@dataclass_with_default(frozen=True)
class MapLoader(TmxLoader):
    _: KW_ONLY = private_init_below()
    background: tuple[DrawingOnScreen | AnimationOnScreen, ...] = default(
        lambda self: self._init_background
    )
    foreground: tuple[tuple[_LayerBottomAndTile, ...], ...] = default(
        lambda self: self._init_foreground
    )
    above_character: tuple[DrawingOnScreen | AnimationOnScreen, ...] = default(
        lambda self: self._init_above_character
    )
    collisions: tuple[PolygonAreaOnScreen, ...] = default(
        lambda self: self._init_collisions
    )
    collision_visuals: tuple[DrawingOnScreen, ...] = default(
        lambda self: self._init_collision_visuals
    )

    def tick(self, time_delta: Millisecond) -> Self:
        background = _tick_layer(self.background, time_delta)
        foreground = tuple(
            tuple(tile.tick(time_delta) for tile in layer)
            for layer in self.foreground
        )
        above_character = _tick_layer(self.above_character, time_delta)
        return replace(
            self,
            background=background,
            above_character=above_character,
            foreground=foreground,
        )

    @cached_property
    def map_size(self) -> Size:
        width = self._tmx.width * self._tile_size.width
        height = self._tmx.height * self._tile_size.height
        return width * height

    def layer_bottom_and_drawing(
        self, character: CharacterOnScreen
    ) -> tuple[_LayerBottomAndTile, ...]:
        character_layer = self._character_layer(character, self.foreground)
        log.debug(
            t"{character.name} layered at {character_layer}", duration=None
        )
        character_bottom = (
            character.drawing_on_screen.visible_rectangle_area_on_screen.bottom
        )
        return tuple(
            _LayerBottomAndTile(resource, character_layer, character_bottom)
            for resource in character.drawing_on_screens
        )

    def _character_layer(
        self,
        character: CharacterOnScreen,
        foreground: tuple[tuple[_LayerBottomAndTile, ...], ...],
    ) -> int:
        for index, layer in enumerate(reversed(foreground)):
            if _below_character_layer(layer, character):
                return index + 1
        return 0

    @property
    def _init_colliders(self) -> tuple[_Collider, ...]:
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
        self, coordinate: _TileCoordinate, obj: TiledObject
    ) -> PolygonAreaOnScreen:
        return self._from_rect(coordinate, obj) or self._from_points(
            coordinate, obj
        )

    def _from_points(
        self, coordinate: _TileCoordinate, obj: TiledObject
    ) -> PolygonAreaOnScreen:
        w, h = self._tile_size
        cx, cy = coordinate
        return PolygonAreaOnScreen(
            tuple(Coordinate(cx * w + x, cy * h + y) for x, y in obj.as_points)
        )

    def _from_rect(
        self, coordinate: _TileCoordinate, obj: TiledObject
    ) -> RectangleAreaOnScreen | None:
        if not is_rect(obj):
            return None

        w, h = self._tile_size
        cx, cy = coordinate
        map_coord = Coordinate(cx * w + obj.x, cy * h + obj.y)
        size = Size(obj.width, obj.height)
        return RectangleAreaOnScreen(map_coord, size)

    def _tile_layers(self, class_name: str) -> tuple[TiledTileLayer, ...]:
        return tuple(
            layer
            for layer in self._all_tile_layers
            if getattr(layer, "class", None) == class_name
            or class_name in layer.name
        )

    @cached_property
    def _all_tile_layers(self) -> tuple[TiledTileLayer, ...]:
        return tuple(self._layer(i) for i in self._tmx.visible_tile_layers)

    def _bottom_and_drawing(
        self, layer: TiledTileLayer
    ) -> tuple[_TileBottomAndDrawings, ...]:
        coordinate_and_drawings = self._drawing(layer)
        coordinate_to_bottom = {
            coordinate: _visible_area(drawing).bottom
            for coordinate, drawing in coordinate_and_drawings.items()
        }
        bottom_and_drawings = tuple(
            _TileBottomAndDrawings(
                self._bottommost(
                    layer, coordinate, drawing, coordinate_to_bottom
                ),
                drawing,
            )
            for coordinate, drawing in coordinate_and_drawings.items()
        )
        return tuple(sorted(bottom_and_drawings, key=lambda t: t.bottommost))

    @property
    def _tile_size(self) -> Size:
        return Size(self._tmx.tilewidth, self._tmx.tileheight)

    def _draw_tile_layers(
        self, class_name: str
    ) -> tuple[DrawingOnScreen | AnimationOnScreen, ...]:
        return tuple(
            drawing
            for layer in self._tile_layers(class_name)
            for drawing in self._drawing(layer).values()
        )

    def _drawing(
        self, layer: TiledTileLayer
    ) -> dict[_TileCoordinate, DrawingOnScreen | AnimationOnScreen]:
        return {
            _TileCoordinate(top, left): self._tile(left, top, gid)
            for left, top, gid in layer
            if gid
        }

    def _tile(
        self, left: int, top: int, gid: _Gid
    ) -> DrawingOnScreen | AnimationOnScreen:
        width, height = self._tile_size
        coordinate = Coordinate(left * width, top * height)
        if frame_infos := self._tmx.tile_properties.get(gid, {}).get("frames"):
            frames = tuple(
                Drawing(self._tmx.images[frame_info.gid])
                for frame_info in frame_infos
            )
            durations = tuple(frame_info.duration for frame_info in frame_infos)
            animation = CyclicAnimation(frames, durations)
            return CyclicAnimationOnScreen(coordinate, animation)
        drawing = Drawing(self._tmx.images[gid])
        return DrawingOnScreen(coordinate, drawing)

    def _class(
        self, layer: TiledTileLayer, coordinate: _TileCoordinate
    ) -> str | None:
        x, y = coordinate
        if 0 <= x < len(layer.data) and 0 <= y < len(layer.data[x]):
            data_id = layer.data[x][y]
            return self._gid_to_cls.get(
                self._tmx.tile_properties.get(data_id, {}).get("id")
            )
        return None

    def _bottommost(
        self,
        layer: TiledTileLayer,
        coordinate: _TileCoordinate,
        drawing: DrawingOnScreen | AnimationOnScreen,
        coordinate_to_bottom: dict[_TileCoordinate, YAxis],
    ) -> YAxis:
        return (
            max(
                coordinate_to_bottom[c]
                for c in self._component(layer, coordinate, cls)
            )
            if (cls := self._class(layer, coordinate))
            else _visible_area(drawing).bottom
        )

    def _component(
        self,
        layer: TiledTileLayer,
        coordinate: _TileCoordinate,
        cls: str,
        visited: set[_TileCoordinate] | None = None,
    ) -> set[_TileCoordinate]:
        visited = (visited or set()) | {coordinate}
        return visited | {
            c
            for neighbor in self._neighbors(layer, coordinate, cls) - visited
            for c in self._component(layer, neighbor, cls, visited)
        }

    def _neighbors(
        self, layer: TiledTileLayer, coordinate: _TileCoordinate, cls: str
    ) -> set[_TileCoordinate]:
        x, y = coordinate
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

    @property
    def _init_background(
        self,
    ) -> tuple[DrawingOnScreen | AnimationOnScreen, ...]:
        return self._draw_tile_layers(config().map.background)

    @property
    def _init_collision_visuals(self) -> tuple[DrawingOnScreen, ...]:
        if config().debug and (
            color := config().debug.collision_rectangle_color
        ):
            return tuple(c.fill(color) for c in self.collisions)
        return ()

    @property
    def _init_foreground(
        self,
    ) -> tuple[tuple[_LayerBottomAndTile, ...], ...]:
        return tuple(
            _foreground_layer(i, tiles)
            for i, layer in enumerate(
                self._tile_layers(config().map.foreground)
            )
            if (tiles := self._bottom_and_drawing(layer))
        )

    @property
    def _init_above_character(
        self,
    ) -> tuple[DrawingOnScreen | AnimationOnScreen, ...]:
        return self._draw_tile_layers(config().map.above_character)

    @property
    def _init_collisions(self) -> tuple[PolygonAreaOnScreen, ...]:
        from_tiles = tuple(
            self._polygon(coordinate, obj)
            for coordinate, obj in self._init_colliders
        )
        from_objects = tuple(
            poly
            for obj in self.get_objects_by_class_name(config().map.collision)
            if (poly := get_geometry(obj))
        )
        return from_tiles + from_objects


def _below_character_layer(
    layer: tuple[_LayerBottomAndTile, ...],
    character: CharacterOnScreen,
) -> bool:
    rect = character.drawing_on_screen.visible_rectangle_area_on_screen
    return any(
        tile.bottommost < rect.bottom
        and rect.collide(_visible_area(tile.resource))
        for tile in layer
    )


def _foreground_layer(
    index: int, tiles: tuple[_TileBottomAndDrawings, ...]
) -> tuple[_LayerBottomAndTile, ...]:
    with_index = tuple(
        _LayerBottomAndTile(drawing, index, bottom) for bottom, drawing in tiles
    )
    sorted_by_bottom = sorted(
        with_index, key=lambda t: t.bottommost, reverse=True
    )
    return tuple(sorted_by_bottom)


type _Gid = int


class _TileCoordinate(NamedTuple):
    top: int
    left: int


class _Collider(NamedTuple):
    coordinate: _TileCoordinate
    obj: TiledObject


class _TileBottomAndDrawings(NamedTuple):
    bottommost: YAxis
    resource: DrawingOnScreen | AnimationOnScreen


@dataclass(frozen=True)
class _LayerBottomAndTile(AnimationOnScreens):
    layer: int
    bottommost: YAxis

    def __lt__(self, other: Self) -> bool:
        if self.layer == other.layer:
            return self.bottommost < other.bottommost
        return self.layer < other.layer


def _visible_area(
    drawing: DrawingOnScreen | AnimationOnScreen,
) -> RectangleAreaOnScreen:
    return drawing.drawing_on_screen.visible_rectangle_area_on_screen


def _tick_layer(
    drawings: tuple[DrawingOnScreen | AnimationOnScreen, ...],
    time_delta: Millisecond,
) -> tuple[DrawingOnScreen | AnimationOnScreen, ...]:
    return tuple(drawing.tick(time_delta) for drawing in drawings)


def drawing_on_screens(
    drawings: tuple[DrawingOnScreen | AnimationOnScreen, ...],
) -> tuple[DrawingOnScreen, ...]:
    return tuple(
        drawing_on_screen
        for drawing in drawings
        for drawing_on_screen in drawing.drawing_on_screens
    )
