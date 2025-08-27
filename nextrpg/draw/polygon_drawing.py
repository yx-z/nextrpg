from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from pygame import SRCALPHA, Surface
from pygame.draw import polygon

from nextrpg.core.color import Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.drawing import Drawing

if TYPE_CHECKING:
    from nextrpg.draw.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass(frozen=True)
class PolygonDrawing:
    points: tuple[Coordinate, ...]
    color: Color
    allow_background_in_debug: bool = True
    bounding_rectangle_area_on_screen: RectangleAreaOnScreen | None = None

    @cached_property
    def drawing(self) -> Drawing:
        return Drawing(
            self._surface,
            allow_background_in_debug=self.allow_background_in_debug,
        )

    def _draw(self, surface: Surface, points: tuple[Coordinate, ...]) -> None:
        polygon(surface, self.color, points)

    @cached_property
    def _surface(self) -> Surface:
        bounding_rect = (
            self.bounding_rectangle_area_on_screen
            or get_bounding_rectangle_area_on_screen(self.points)
        )
        surface = Surface(bounding_rect.size, SRCALPHA)
        negated = tuple(p - bounding_rect.top_left for p in self.points)
        self._draw(surface, negated)
        return surface


def get_bounding_rectangle_area_on_screen(
    points: tuple[Coordinate, ...],
) -> RectangleAreaOnScreen:
    from nextrpg.draw.rectangle_area_on_screen import RectangleAreaOnScreen

    min_x = min(c.left_value for c in points)
    min_y = min(c.top_value for c in points)
    max_x = max(c.left_value for c in points)
    max_y = max(c.top_value for c in points)
    coordinate = Coordinate(min_x, min_y)
    # The bounding rectangle must have a size of at least (1, 1).
    # Otherwise, no surface to blit.
    # This is useful for drawing vertical/horizontal lines.
    width = max(max_x - min_x, 1)
    height = max(max_y - min_y, 1)
    size = Size(width, height)
    return RectangleAreaOnScreen(coordinate, size)
