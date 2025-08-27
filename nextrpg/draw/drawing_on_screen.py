from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from pygame import Surface

from nextrpg.core.color import Alpha
from nextrpg.draw.drawing import Drawing
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Height, Size, Width
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.sizable import Sizable


@dataclass(frozen=True)
class DrawingOnScreen(Sizable):
    top_left: Coordinate
    drawing: Drawing

    @property
    def rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        return RectangleAreaOnScreen(self.top_left, self.drawing.size)

    @cached_property
    def visible_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        shift = self.drawing.visible_rectangle_area_on_screen.top_left
        size = self.drawing.visible_rectangle_area_on_screen.size
        return RectangleAreaOnScreen(self.top_left + shift, size)

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

    def __sub__(
        self, other: Coordinate | Size | Width | Height
    ) -> DrawingOnScreen:
        return self + -other
