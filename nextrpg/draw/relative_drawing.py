from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Self

from nextrpg.core.anchor import Anchor
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.drawing import Drawing

if TYPE_CHECKING:
    from nextrpg.draw.drawing_group import DrawingGroup


@dataclass(frozen=True)
class RelativeDrawing:
    drawing: Drawing | DrawingGroup
    shift: Size
    anchor: Anchor = Anchor.TOP_LEFT

    def add_tag(self, tag: Hashable) -> Self:
        drawing = self.drawing.add_tag(tag)
        return replace(self, drawing=drawing)

    @property
    def tags(self) -> tuple[Hashable, ...]:
        return self.drawing.tags

    def top_left(self, origin: Coordinate) -> Coordinate:
        match self.anchor:
            case Anchor.TOP_LEFT:
                extra = Size(0, 0)
            case Anchor.TOP_CENTER:
                extra = Size(-self.drawing.width.value / 2, 0)
            case Anchor.TOP_RIGHT:
                extra = Size(-self.drawing.width.value, 0)
            case Anchor.CENTER_LEFT:
                extra = Size(0, -self.drawing.height.value / 2)
            case Anchor.CENTER:
                extra = Size(
                    -self.drawing.width.value / 2,
                    -self.drawing.height.value / 2,
                )
            case Anchor.CENTER_RIGHT:
                extra = Size(
                    -self.drawing.width.value, -self.drawing.height.value / 2
                )
            case Anchor.BOTTOM_LEFT:
                extra = Size(0, -self.drawing.height.value)
            case Anchor.BOTTOM_CENTER:
                extra = Size(
                    -self.drawing.width.value / 2, -self.drawing.height.value
                )
            case Anchor.BOTTOM_RIGHT:
                extra = Size(
                    -self.drawing.width.value, -self.drawing.height.value
                )
        return origin + extra + self.shift
