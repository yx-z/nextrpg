from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from pygame import Surface

from nextrpg.core.color import Alpha
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Height, Size, Width
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing import Drawing

if TYPE_CHECKING:
    from nextrpg.draw.rectangle_area import RectangleArea


@dataclass(frozen=True)
class DrawingOnScreen(Sizable):
    top_left: Coordinate
    drawing: Drawing

    @property
    def rectangle_on_screen(self) -> RectangleArea:
        from nextrpg.draw.rectangle_area import RectangleArea

        return RectangleArea(self.top_left, self.drawing.size)

    @cached_property
    def visible_rectangle_on_screen(self) -> RectangleArea:
        from nextrpg.draw.rectangle_area import RectangleArea

        shift = self.drawing.visible_rectangle.top_left
        size = self.drawing.visible_rectangle.size
        return RectangleArea(self.top_left + shift, size)

    @property
    def pygame(self) -> tuple[Surface, Coordinate]:
        return self.drawing.pygame, self.top_left

    def set_alpha(self, alpha: Alpha) -> DrawingOnScreen:
        return DrawingOnScreen(self.top_left, self.drawing.set_alpha(alpha))

    @property
    def size(self) -> Size:
        return self.drawing.size

    def __add__(
        self, other: Coordinate | Size | Width | Height
    ) -> DrawingOnScreen:
        return DrawingOnScreen(self.top_left + other, self.drawing)

    def add_fast(self, other: Coordinate) -> DrawingOnScreen:
        left, top = self.top_left
        shift_left, shift_top = other
        coord = Coordinate(left + shift_left, top + shift_top)
        return DrawingOnScreen(coord, self.drawing)

    def __sub__(
        self, other: Coordinate | Size | Width | Height
    ) -> DrawingOnScreen:
        return self + -other
