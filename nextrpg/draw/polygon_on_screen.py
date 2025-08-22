from __future__ import annotations

from dataclasses import KW_ONLY
from functools import cached_property
from typing import TYPE_CHECKING

from pygame import Mask
from pygame.mask import from_surface

from nextrpg.core.color import BLACK, Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.dimension import Height, Pixel, Size, Width
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.polygon_drawing import PolygonDrawing, get_bounding_rectangle

if TYPE_CHECKING:
    from nextrpg.draw.rectangle_on_screen import RectangleOnScreen


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
        return get_bounding_rectangle(self.points)

    def fill(
        self, color: Color, allow_background_in_debug: bool = False
    ) -> DrawingOnScreen:
        drawing = PolygonDrawing(
            self.points,
            color,
            allow_background_in_debug,
            self.bounding_rectangle,
        )
        return DrawingOnScreen(self.top_left, drawing.drawing)

    def line(
        self, color: Color, allow_background_in_debug: bool = False
    ) -> DrawingOnScreen:
        drawing = PolygonDrawing(
            self.points,
            color,
            allow_background_in_debug,
            self.bounding_rectangle,
            line_only=True,
        )
        return DrawingOnScreen(self.top_left, drawing.drawing)

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
