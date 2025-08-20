from __future__ import annotations

from dataclasses import KW_ONLY
from functools import cached_property
from typing import Callable, override

from pygame import SRCALPHA, Mask, Rect, Surface
from pygame.draw import lines, polygon, rect
from pygame.mask import from_surface

from nextrpg.core.color import BLACK, Color
from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.dimension import Height, Pixel, Size, Width
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing import Drawing, TransparentDrawing
from nextrpg.draw.drawing_on_screen import DrawingOnScreen


class PolygonDrawing(TransparentDrawing):
    def __init__(self, points: tuple[Coordinate, ...], color: Color) -> None:
        fill = _fill_polygon(color)
        surface = _draw_polygon(points, fill)
        _set_resource_color_and_color_key(self, surface, color)


@dataclass_with_init(frozen=True)
class PolygonOnScreen(Sizable):
    points: tuple[Coordinate, ...]
    closed: bool = True
    _: KW_ONLY = not_constructor_below()
    top_left: Coordinate = default(
        lambda self: self.bounding_rectangle.top_left
    )
    size: Size = default(lambda self: self.bounding_rectangle.size)

    @cached_property
    def length(self) -> Pixel:
        distances = tuple(
            p.distance(np) for p, np in zip(self.points, self.points[1:])
        )
        length = sum(distances)
        if self.closed:
            return length + self.points[0].distance(self.points[-1])
        return length

    @cached_property
    def bounding_rectangle(self) -> RectangleOnScreen:
        return _bounding_rectangle(self.points)

    def fill(
        self, color: Color, allow_background_in_debug: bool = False
    ) -> DrawingOnScreen:
        fill = _fill_polygon(color)
        return self._drawing_on_screen(
            fill, allow_background_in_debug=allow_background_in_debug
        )

    def line(
        self, color: Color, allow_background_in_debug: bool = False
    ) -> DrawingOnScreen:
        def _line(surface: Surface, points: tuple[Coordinate, ...]) -> None:
            lines(surface, color, self.closed, points)

        return self._drawing_on_screen(
            _line, allow_background_in_debug=allow_background_in_debug
        )

    def collide(self, poly: PolygonOnScreen) -> bool:
        if not self.bounding_rectangle.collide(poly.bounding_rectangle):
            return False
        offset = (
            self.bounding_rectangle.top_left - poly.bounding_rectangle.top_left
        )
        return bool(self._mask.overlap(poly._mask, offset))

    def __contains__(self, coordinate: Coordinate) -> bool:
        x, y = coordinate - self.bounding_rectangle.top_left
        width, height = self._mask.get_size()
        if 0 <= x < width and 0 <= y < height:
            return bool(self._mask.get_at((x, y)))
        return False

    def __add__(
        self, other: Coordinate | Size | Width | Height
    ) -> PolygonOnScreen:
        points = tuple(p + other for p in self.points)
        return PolygonOnScreen(points, self.closed)

    def __sub__(
        self, other: Coordinate | Size | Width | Height
    ) -> PolygonOnScreen:
        return self + -other

    @cached_property
    def _mask(self) -> Mask:
        surface = self.fill(BLACK).drawing.pygame
        return from_surface(surface)

    def _drawing_on_screen(
        self,
        method: Callable[[Surface, tuple[Coordinate, ...]], None],
        allow_background_in_debug: bool,
    ) -> DrawingOnScreen:
        surface = _draw_polygon(self.points, method, self.bounding_rectangle)
        drawing = Drawing(
            surface, allow_background_in_debug=allow_background_in_debug
        )
        return DrawingOnScreen(self.bounding_rectangle.top_left, drawing)


class RectangleDrawing(TransparentDrawing):
    def __init__(
        self, size: Size, color: Color, border_radius: Pixel | None = None
    ) -> None:
        surface = Surface(size, SRCALPHA)
        rectangle = Rect(ORIGIN, size)
        rect(surface, color, rectangle, border_radius=border_radius or -1)
        _set_resource_color_and_color_key(self, surface, color)


class RectangleOnScreen(PolygonOnScreen):
    def __init__(self, top_left: Coordinate, size: Size) -> None:
        object.__setattr__(self, "top_left", top_left)
        object.__setattr__(self, "size", size)

    @property
    def points(self) -> tuple[Coordinate, ...]:
        return (
            self.top_left,
            self.top_right,
            self.bottom_right,
            self.bottom_left,
        )

    @override
    def collide(self, poly: PolygonOnScreen) -> bool:
        if not isinstance(poly, RectangleOnScreen):
            return super().collide(poly)

        return (
            self.top_left.left < poly.top_right.left
            and self.top_right.left > poly.top_left.left
            and self.top_left.top < poly.bottom_right.top
            and self.bottom_right.top > poly.top_left.top
        )

    @override
    def __contains__(self, coordinate: Coordinate) -> bool:
        return (
            self.left < coordinate.left < self.right
            and self.top < coordinate.top < self.bottom
        )

    def __add__(
        self, other: Coordinate | Size | Width | Height
    ) -> RectangleOnScreen:
        return RectangleOnScreen(self.top_left + other, self.size)

    def __sub__(
        self, other: Coordinate | Size | Width | Height
    ) -> RectangleOnScreen:
        return RectangleOnScreen(self.top_left - other, self.size)

    def fill(
        self, color: Color, border_radius: Pixel | None = None
    ) -> DrawingOnScreen:
        return DrawingOnScreen(
            self.top_left, RectangleDrawing(self.size, color, border_radius)
        )


def _bounding_rectangle(points: tuple[Coordinate, ...]) -> RectangleOnScreen:
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


def _draw_polygon(
    points: tuple[Coordinate, ...],
    method: Callable[[Surface, tuple[Coordinate, ...]], None],
    bounding_rectangle: RectangleOnScreen | None = None,
) -> Surface:
    bounding_rectangle = bounding_rectangle or _bounding_rectangle(points)
    surface = Surface(bounding_rectangle.size, SRCALPHA)
    negated = tuple(p - bounding_rectangle.top_left for p in points)
    method(surface, negated)
    return surface


def _set_resource_color_and_color_key[T](
    self: T, surface: Surface, color: Color
) -> None:
    object.__setattr__(self, "resource", surface)
    object.__setattr__(self, "color", color)
    object.__setattr__(self, "color_key", None)


def _fill_polygon(
    color: Color,
) -> Callable[[Surface, tuple[Coordinate, ...]], None]:
    def fill(surface: Surface, points: tuple[Coordinate, ...]) -> None:
        polygon(surface, color, points)

    return fill
