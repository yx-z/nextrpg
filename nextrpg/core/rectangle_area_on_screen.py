from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg.core.area_on_screen import AreaOnScreen
from nextrpg.core.color import Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Height, Pixel, Size, Width
from nextrpg.core.polygon_area_on_screen import PolygonAreaOnScreen

if TYPE_CHECKING:
    from nextrpg.draw.drawing_on_screen import DrawingOnScreen


@dataclass(frozen=True)
class RectangleAreaOnScreen(AreaOnScreen):
    top_left: Coordinate
    size: Size

    @property
    def pygame(self) -> tuple[Coordinate, Size]:
        return self.top_left, self.size

    @override
    def collide(self, area: AreaOnScreen) -> bool:
        if not isinstance(area, RectangleAreaOnScreen):
            return self._polygon.collide(area)
        return (
            self.top_left.left < area.top_right.left
            and self.top_right.left > area.top_left.left
            and self.top_left.top < area.bottom_right.top
            and self.bottom_right.top > area.top_left.top
        )

    @override
    def __contains__(self, coordinate: Coordinate) -> bool:
        return (
            self.left < coordinate.left < self.right
            and self.top < coordinate.top < self.bottom
        )

    @override
    def __add__(self, other: Coordinate | Size | Width | Height) -> Self:
        coordinate = self.top_left + other
        return replace(self, top_left=coordinate)

    @override
    def fill(
        self,
        color: Color,
        allow_background_in_debug: bool = True,
        border_radius: Pixel | None = None,
    ) -> DrawingOnScreen:
        from nextrpg.draw.drawing_on_screen import DrawingOnScreen
        from nextrpg.draw.rectangle_drawing import RectangleDrawing

        rect = RectangleDrawing(
            self.size, color, border_radius, allow_background_in_debug
        )
        return DrawingOnScreen(self.top_left, rect.drawing)

    @cached_property
    def points(self) -> tuple[Coordinate, ...]:
        return (
            self.top_left,
            self.top_right,
            self.bottom_right,
            self.bottom_left,
        )

    @cached_property
    def _polygon(self) -> PolygonAreaOnScreen:
        return PolygonAreaOnScreen(self.points)
