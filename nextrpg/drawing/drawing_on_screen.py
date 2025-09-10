from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from pygame import Surface

from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.color import Alpha
from nextrpg.drawing.drawing import Drawing
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Height, Size, Width
from nextrpg.geometry.direction import DirectionalOffset
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass(frozen=True)
class DrawingOnScreen(AnimationOnScreenLike):
    top_left: Coordinate
    drawing: Drawing

    @cached_property
    def visible_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        shift = self.drawing.visible_rectangle_area_on_screen.top_left
        size = self.drawing.visible_rectangle_area_on_screen.size
        coordinate = self.top_left + shift
        return coordinate.anchor(size).rectangle_area_on_screen

    @property
    def pygame(self) -> tuple[Surface, Coordinate]:
        return self.drawing.pygame, self.top_left

    def blur(self, radius: int | float) -> Self:
        drawing = self.drawing.blur(radius)
        return replace(self, drawing=drawing)

    def with_alpha(self, alpha: Alpha) -> Self:
        drawing = self.drawing.with_alpha(alpha)
        return replace(self, top_left=self.top_left, drawing=drawing)

    @property
    def size(self) -> Size:
        return self.drawing.size

    def __add__(
        self, other: Coordinate | Size | Width | Height | DirectionalOffset
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
        self, other: Coordinate | Size | Width | Height | DirectionalOffset
    ) -> DrawingOnScreen:
        return self + -other

    @property
    def drawing_on_screen(self) -> DrawingOnScreen:
        return self

    @property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return (self,)

    def tick(self, time_delta: Millisecond) -> Self:
        return self

    @property
    def is_complete(self) -> bool:
        return True
