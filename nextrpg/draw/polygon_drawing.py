from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Callable

from pygame import SRCALPHA, Surface
from pygame.draw import lines, polygon

from nextrpg.core.color import Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.transparent_drawing import TransparentDrawing

if TYPE_CHECKING:
    from nextrpg.draw.rectangle_on_screen import RectangleOnScreen


@dataclass(frozen=True)
class PolygonDrawing:
    points: tuple[Coordinate, ...]
    color: Color
    allow_background_in_debug: bool = False
    bounding_rectangle: RectangleOnScreen | None = None
    line_only: bool = False
    tags: tuple[Hashable, ...] = ()

    @cached_property
    def drawing(self) -> TransparentDrawing:
        if self.line_only:
            fill = self._line
        else:
            fill = self._fill
        surface = self._draw_polygon(fill)
        return TransparentDrawing(
            resource=surface,
            allow_background_in_debug=self.allow_background_in_debug,
            tags=self.tags,
            color=self.color,
        )

    @cached_property
    def _line(self) -> Callable[[Surface, list[Coordinate]], None]:
        def line(surface: Surface, points: list[Coordinate]) -> None:
            lines(surface, self.color, closed=False, points=points)

        return line

    @cached_property
    def _fill(self) -> Callable[[Surface, list[Coordinate]], None]:
        def fill(surface: Surface, points: list[Coordinate]) -> None:
            polygon(surface, self.color, points)

        return fill

    def _draw_polygon(
        self, method: Callable[[Surface, list[Coordinate]], None]
    ) -> Surface:
        bounding_rect = self.bounding_rectangle or get_bounding_rectangle(
            self.points
        )
        surface = Surface(bounding_rect.size, SRCALPHA)
        negated = [p - bounding_rect.top_left for p in self.points]
        method(surface, negated)
        return surface


def get_bounding_rectangle(points: tuple[Coordinate, ...]) -> RectangleOnScreen:
    from nextrpg.draw.rectangle_on_screen import RectangleOnScreen

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
    return RectangleOnScreen(coordinate, size)
