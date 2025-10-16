from dataclasses import dataclass, replace
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.anchor import Anchor
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import (
    ZERO_SIZE,
    HeightScaling,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)


@dataclass(frozen=True)
class RelativeDrawing:
    drawing: AnimationLike
    shift: Size
    anchor: Anchor = Anchor.TOP_LEFT

    def tick(self, time_delta: Millisecond) -> Self:
        drawing = self.drawing.tick(time_delta)
        return replace(self, drawing=drawing)

    def top_left(self, origin: Coordinate) -> Coordinate:
        match self.anchor:
            case Anchor.TOP_LEFT:
                extra = ZERO_SIZE
            case Anchor.TOP_CENTER:
                extra = self.drawing.width / 2
            case Anchor.TOP_RIGHT:
                extra = self.drawing.width
            case Anchor.CENTER_LEFT:
                extra = self.drawing.height / 2
            case Anchor.CENTER:
                extra = self.drawing.size / WidthAndHeightScaling(2)
            case Anchor.CENTER_RIGHT:
                extra = self.drawing.size / HeightScaling(2)
            case Anchor.BOTTOM_LEFT:
                extra = self.drawing.height
            case Anchor.BOTTOM_CENTER:
                extra = self.drawing.size / WidthScaling(2)
            case Anchor.BOTTOM_RIGHT:
                extra = self.drawing.size
        return origin + self.shift - extra

    def flip(self, horizontal: bool = False, vertical: bool = False) -> Self:
        drawing = self.drawing.flip(horizontal, vertical)
        shift = self.shift
        if horizontal:
            shift = shift.negate_width
        if vertical:
            shift = shift.negate_height
        anchor = -self.anchor
        return replace(self, drawing=drawing, shift=shift, anchor=anchor)
