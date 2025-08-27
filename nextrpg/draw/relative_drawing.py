from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from nextrpg.draw.drawing import Drawing
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import (
    ZERO_SIZE,
    HeightScaling,
    Size,
    WidthAndHeightScaling,
    WidthScaling,
)

if TYPE_CHECKING:
    from nextrpg.draw.drawing_group import DrawingGroup


class Anchor(Enum):
    TOP_LEFT = auto()
    TOP_CENTER = auto()
    TOP_RIGHT = auto()
    CENTER_LEFT = auto()
    CENTER = auto()
    CENTER_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_CENTER = auto()
    BOTTOM_RIGHT = auto()


@dataclass(frozen=True)
class RelativeDrawing:
    drawing: Drawing | DrawingGroup
    shift: Size
    anchor: Anchor = Anchor.TOP_LEFT

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
