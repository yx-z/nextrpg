from dataclasses import dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import Self, override

from pygame import Surface

from nextrpg.drawing.animation_on_screen_like import (
    AnimationOnScreenLike,
)
from nextrpg.drawing.color import Alpha
from nextrpg.drawing.drawing import Drawing
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Height, Size, Width
from nextrpg.geometry.direction import DirectionalOffset
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass(frozen=True)
class DrawingOnScreen(AnimationOnScreenLike):
    top_left_input: Coordinate
    drawing: Drawing

    @override
    @cached_property
    def visible_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        shift = self.drawing.visible_rectangle_area_on_screen.top_left
        size = self.drawing.visible_rectangle_area_on_screen.size
        coordinate = self.top_left + shift
        return coordinate.anchor(size).rectangle_area_on_screen

    @cached_property
    def pygame(self) -> tuple[Surface, Coordinate]:
        return self.drawing.pygame, self.top_left

    def blur(self, radius: int) -> Self:
        drawing = self.drawing.blur(radius)
        return replace(self, drawing=drawing)

    def alpha(self, alpha: Alpha) -> Self:
        drawing = self.drawing.alpha(alpha)
        return replace(self, drawing=drawing)

    def to_file(self, file: Path) -> None:
        self.drawing.to_file(file)

    def __add__(
        self, other: Coordinate | Size | Width | Height | DirectionalOffset
    ) -> DrawingOnScreen:
        top_left = self.top_left + other
        return replace(self, top_left_input=top_left)

    def __sub__(
        self, other: Coordinate | Size | Width | Height | DirectionalOffset
    ) -> DrawingOnScreen:
        return self + -other

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return (self,)

    @override
    @cached_property
    def size(self) -> Size:
        return self.drawing.size
