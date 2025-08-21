from __future__ import annotations

from typing import override

from nextrpg.core.color import Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Height, Pixel, Size, Width
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.polygon_on_screen import PolygonOnScreen
from nextrpg.draw.rectangle_drawing import RectangleDrawing


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
