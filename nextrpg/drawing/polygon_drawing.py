from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, override

from pygame import SRCALPHA, Surface
from pygame.draw import polygon

from nextrpg.core.metadata import METADATA_CACHE_KEY
from nextrpg.core.save import LoadFromSave
from nextrpg.drawing.color import Color
from nextrpg.drawing.drawing import Drawing
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polygon_area_on_screen import (
    get_bounding_rectangle_area_on_screen,
)
from nextrpg.geometry.size import Size

if TYPE_CHECKING:
    from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass(frozen=True)
class PolygonDrawing(LoadFromSave):
    points: tuple[Coordinate, ...]
    color: Color
    allow_background_in_debug: bool = True
    bounding_rectangle_area_on_screen: RectangleAreaOnScreen | None = None

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        points = [p.save_data for p in self.points]
        return {
            "points": points,
            "color": self.color.save_data,
            "allow_background_in_debug": self.allow_background_in_debug,
        }

    @override
    @classmethod
    def load_this_class_from_save(cls, data: dict[str, Any]) -> Self:
        points = tuple(Coordinate.load_from_save(p) for p in data["points"])
        color = Color.load_from_save(data["color"])
        allow_background_in_debug = data["allow_background_in_debug"]
        return cls(points, color, allow_background_in_debug)

    @cached_property
    def drawing(self) -> Drawing:
        metadata = (
            METADATA_CACHE_KEY,
            ("points", self.points),
            ("color", self.color),
        )
        return Drawing(self._surface, self.allow_background_in_debug, metadata)

    def _draw(self, surface: Surface, points: tuple[Coordinate, ...]) -> None:
        polygon(surface, self.color.pygame, points)

    @cached_property
    def _surface(self) -> Surface:
        bounding_rect = (
            self.bounding_rectangle_area_on_screen
            or get_bounding_rectangle_area_on_screen(self.points)
        )
        # Needed to draw the pixels at edge.
        margin = Size(1, 1)
        surface = Surface(bounding_rect.size + margin, SRCALPHA).convert_alpha()
        negated = tuple(p - bounding_rect.top_left for p in self.points)
        self._draw(surface, negated)
        return surface
