from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

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

    def set_alpha(self, alpha: Alpha) -> Self:
        drawing = self.drawing.set_alpha(alpha)
        return replace(self, top_left=self.top_left, drawing=drawing)

    @property
    def size(self) -> Size:
        return self.drawing.size

    def __add__(
        self, other: Coordinate | Size | Width | Height
    ) -> DrawingOnScreen:
        top_left = self.top_left + other
        return replace(self, top_left=top_left, drawing=self.drawing)

    def add_fast(self, other: Coordinate) -> DrawingOnScreen:
        return DrawingOnScreen(
            Coordinate(
                self.top_left.left_value + other.left_value,
                self.top_left.top_value + other.top_value,
            ),
            self.drawing,
        )

    def __sub__(
        self, other: Coordinate | Size | Width | Height
    ) -> DrawingOnScreen:
        return self + -other
