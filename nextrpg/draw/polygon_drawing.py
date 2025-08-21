from __future__ import annotations

from typing import Any, TYPE_CHECKING, Callable

from pygame import SRCALPHA, Surface
from pygame.draw import lines, polygon

from nextrpg.core.color import Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.transparent_drawing import TransparentDrawing

if TYPE_CHECKING:
    from nextrpg.draw.rectangle_on_screen import RectangleOnScreen


class PolygonDrawing(TransparentDrawing):
    points: tuple[Coordinate, ...]
    line_only: bool

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PolygonDrawing):
            return False
        return (
            self.points == other.points
            and self.color == other.color
            and self.line_only == other.line_only
        )

    def __init__(
        self,
        points: tuple[Coordinate, ...],
        color: Color,
        allow_background_in_debug: bool = False,
        bounding_rectangle: RectangleOnScreen | None = None,
        line_only: bool = False,
    ) -> None:
        if line_only:
            fill = _line(color)
        else:
            fill = _fill(color)

        surface = _draw_polygon(points, fill, bounding_rectangle)
        # Drawing
        object.__setattr__(self, "resource", surface)
        object.__setattr__(self, "color_key", None)
        object.__setattr__(self, "convert_alpha", None)
        object.__setattr__(
            self, "allow_background_in_debug", allow_background_in_debug
        )
        # TransparentDrawing
        object.__setattr__(self, "color", color)
        # PolygonDrawing
        object.__setattr__(self, "points", points)
        object.__setattr__(self, "line_only", line_only)


def _draw_polygon(
    points: tuple[Coordinate, ...],
    method: Callable[[Surface, tuple[Coordinate, ...]], None],
    bounding_rect: RectangleOnScreen | None,
) -> Surface:
    bounding_rect = bounding_rect or get_bounding_rectangle(points)
    surface = Surface(bounding_rect.size, SRCALPHA)
    negated = tuple(p - bounding_rect.top_left for p in points)
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


def _line(color: Color) -> Callable[[Surface, tuple[Coordinate, ...]], None]:
    def line(surface: Surface, points: tuple[Coordinate, ...]) -> None:
        lines(surface, color, closed=False, points=points)

    return line


def _fill(color: Color) -> Callable[[Surface, tuple[Coordinate, ...]], None]:
    def fill(surface: Surface, points: tuple[Coordinate, ...]) -> None:
        polygon(surface, color, points)

    return fill
