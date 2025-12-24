from dataclasses import dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Self, override

from pygame import Surface

from nextrpg.drawing.color import Alpha
from nextrpg.drawing.drawing import EMPTY_DRAWING, Drawing
from nextrpg.drawing.sprite import BlurRadius
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.directional_offset import DirectionalOffset
from nextrpg.geometry.size import Height, Size, Width

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_on_screens import DrawingOnScreens


@dataclass(frozen=True)
class DrawingOnScreen(SpriteOnScreen):
    coordinate: Coordinate
    drawing: Drawing
    anchor: Anchor = Anchor.TOP_LEFT

    @override
    @cached_property
    def top_left(self) -> Coordinate:
        # Optimize/Shortcut for the most common/default case.
        if self.anchor is Anchor.TOP_LEFT:
            return self.coordinate
        return self.coordinate.as_anchor_of(self, self.anchor).top_left

    @override
    @cached_property
    def pygame(self) -> tuple[Surface, Coordinate]:
        return self.drawing.pygame, self.top_left

    def blur(self, radius: BlurRadius) -> Self:
        drawing = self.drawing.blur(radius)
        return replace(self, drawing=drawing)

    def alpha(self, alpha: Alpha) -> Self:
        drawing = self.drawing.alpha(alpha)
        return replace(self, drawing=drawing)

    def to_file(self, file: str | Path) -> None:
        self.drawing.to_file(file)

    @override
    def __add__(
        self, other: Coordinate | Size | Width | Height | DirectionalOffset
    ) -> Self:
        coordinate = self.coordinate + other
        return replace(self, coordinate=coordinate)

    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        from nextrpg.drawing.drawing_on_screens import DrawingOnScreens

        return DrawingOnScreens((self,))

    @override
    @cached_property
    def size(self) -> Size:
        return self.drawing.size


EMPTY_DRAWING_ON_SCREEN = EMPTY_DRAWING.drawing_on_screen(ORIGIN)
