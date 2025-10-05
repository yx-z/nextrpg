from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from pygame import Surface

from nextrpg.drawing.abstract_animation_on_screen_like import (
    AbstractAnimationOnScreenLike,
)
from nextrpg.drawing.color import Alpha
from nextrpg.drawing.drawing import Drawing
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Height, Size, Width
from nextrpg.geometry.direction import DirectionalOffset
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass(frozen=True)
class DrawingOnScreen(AbstractAnimationOnScreenLike):
    top_left_input: Coordinate
    drawing: Drawing

    @override
    @cached_property
    def visible_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        shift = self.drawing.visible_rectangle_area_on_screen.top_left
        size = self.drawing.visible_rectangle_area_on_screen.size
        coordinate = self.top_left + shift
        return coordinate.anchor(size).rectangle_area_on_screen

    @property
    def pygame(self) -> tuple[Surface, Coordinate]:
        return self.drawing.pygame, self.top_left_input

    def blur(self, radius: int) -> Self:
        drawing = self.drawing.blur(radius)
        return replace(self, drawing=drawing)

    def with_alpha(self, alpha: Alpha) -> Self:
        drawing = self.drawing.with_alpha(alpha)
        return replace(self, drawing=drawing)

    def __add__(
        self, other: Coordinate | Size | Width | Height | DirectionalOffset
    ) -> DrawingOnScreen:
        top_left = self.top_left_input + other
        return replace(self, top_left_input=top_left)

    def add_fast(self, other: Coordinate) -> DrawingOnScreen:
        return DrawingOnScreen(
            Coordinate(
                self.top_left_input.left_value + other.left_value,
                self.top_left_input.top_value + other.top_value,
            ),
            self.drawing,
        )

    def __sub__(
        self, other: Coordinate | Size | Width | Height | DirectionalOffset
    ) -> DrawingOnScreen:
        return self + -other

    @property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return (self,)

    @override
    @property
    def size(self) -> Size:
        return self.drawing.size
