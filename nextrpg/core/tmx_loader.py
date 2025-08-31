from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from pytmx import TiledMap, TiledObject, TiledObjectGroup, TiledTileLayer, \
    load_pygame

from nextrpg.core.log import Log
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.polygon_area_on_screen import PolygonAreaOnScreen
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

log = Log()

@dataclass(frozen=True)
class TmxLoader:
    file: Path

    def get_object(self, name: str) -> TiledObject:
        for obj in self._all_objects:
            if obj.name == name:
                return obj
        raise RuntimeError(f"Object {name} not found.")

    def get_objects_by_class_name(
        self, class_name: str
    ) -> tuple[TiledObject, ...]:
        return tuple(obj for obj in self._all_objects if obj.type == class_name)

    @cached_property
    def _tmx(self) -> TiledMap:
        log.debug(t"Loading {self.file}")
        return load_pygame(str(self.file))

    @cached_property
    def _all_objects(self) -> tuple[TiledObject, ...]:
        return tuple(
            obj
            for i in self._tmx.visible_object_groups
            for obj in self._layer(i)
        )


    def _layer(self, index: int) -> TiledTileLayer | TiledObjectGroup:
        return self._tmx.layers[index]


def _is_rect(obj: TiledObject) -> bool:
    return obj.x is not None and obj.y is not None and obj.width and obj.height


def get_geometry(
    obj: TiledObject,
) -> PolygonAreaOnScreen | PolylineOnScreen | RectangleAreaOnScreen | None:
    if hasattr(obj, "points"):
        points = tuple(Coordinate(x, y) for x, y in obj.points)
        if obj.closed:
            return PolygonAreaOnScreen(points)
        return PolylineOnScreen(points)
    if _is_rect(obj):
        coordinate = Coordinate(obj.x, obj.y)
        size = Size(obj.width, obj.height)
        return coordinate.anchor(size).rectangle_area_on_screen
    return None
