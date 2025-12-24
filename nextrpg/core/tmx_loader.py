from dataclasses import KW_ONLY
from functools import cached_property
from pathlib import Path

from pytmx import (
    TiledImageLayer,
    TiledMap,
    TiledObject,
    TiledObjectGroup,
    TiledTileLayer,
    load_pygame,
)

from nextrpg.core.cached_decorator import cached
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.metadata import METADATA_CACHE_KEY
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polygon_area_on_screen import PolygonAreaOnScreen
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.size import Size


def get_geometry(
    obj: TiledObject,
) -> PolygonAreaOnScreen | PolylineOnScreen | RectangleAreaOnScreen | None:
    if hasattr(obj, "points"):
        points = tuple(Coordinate(x, y) for x, y in obj.points)
        if obj.closed:
            return PolygonAreaOnScreen(points)
        return PolylineOnScreen(points)
    if is_rect(obj):
        coordinate = Coordinate(obj.x, obj.y)
        size = Size(obj.width, obj.height)
        return coordinate.as_top_left_of(size).rectangle_area_on_screen
    return None


def get_coordinate(obj: TiledObject) -> Coordinate:
    return Coordinate(obj.x, obj.y)


@cached(lambda resource_config: resource_config.tmx_loader_cache_size)
@dataclass_with_default(frozen=True)
class TmxLoader:
    file: str | Path
    _: KW_ONLY = private_init_below()
    _tmx: TiledMap = default(lambda self: load_pygame(str(self.file)))

    def get_object(self, name: str) -> TiledObject:
        for obj in self.all_objects:
            if obj.name == name:
                return obj
        raise RuntimeError(f"Object {name} not found.")

    def get_objects_by_class_name(
        self, class_name: str
    ) -> tuple[TiledObject, ...]:
        return tuple(obj for obj in self.all_objects if obj.type == class_name)

    def image_layer(self, name: str) -> DrawingOnScreen:
        layer = self._tmx.get_layer_by_name(name)
        assert isinstance(
            layer, TiledImageLayer
        ), f"Require {name} to be a TiledImageLayer"
        left = getattr(layer, "offsetx", 0)
        top = getattr(layer, "offsety", 0)
        coordinate = Coordinate(left, top)
        metadata = (METADATA_CACHE_KEY, ("file", self.file), ("layer", layer))
        drawing = Drawing(layer.image, metadata=metadata)
        return drawing.drawing_on_screen(coordinate)

    @cached_property
    def all_objects(self) -> tuple[TiledObject, ...]:
        return tuple(
            obj
            for index in self._tmx.visible_object_groups
            for obj in self._layer(index)
        )

    def _layer(
        self, index: int
    ) -> TiledTileLayer | TiledImageLayer | TiledObjectGroup:
        return self._tmx.layers[index]


def is_rect(obj: TiledObject) -> bool:
    return obj.x is not None and obj.y is not None and obj.width and obj.height
