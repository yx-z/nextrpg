from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self

from nextrpg.draw.anchor import Anchor
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.relative_drawing import RelativeDrawing
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.draw.drawing_group_on_screen import DrawingGroupOnScreen


@dataclass(frozen=True)
class DrawingGroup(Sizable):
    relative_drawings: tuple[RelativeDrawing, ...]

    def shift(
        self, shift: Size, anchor: Anchor = Anchor.TOP_LEFT
    ) -> RelativeDrawing:
        return RelativeDrawing(self, shift, anchor)

    @cached_property
    def drawings(self) -> tuple[Drawing, ...]:
        res: list[Drawing] = []
        for relative in self.relative_drawings:
            match relative.drawing:
                case DrawingGroup() as drawing_group:
                    res += drawing_group.drawings
                case Drawing() as drawing:
                    res.append(drawing)
        return tuple(res)

    def drawing_on_screens(
        self, origin: Coordinate
    ) -> tuple[DrawingOnScreen, ...]:
        from nextrpg.draw.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(origin, self).drawing_on_screens

    def group_on_screen(self, origin: Coordinate) -> DrawingGroupOnScreen:
        from nextrpg.draw.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(origin, self)

    @property
    def size(self) -> Size:
        return self._drawing_group_on_screen.size

    @property
    def top_left(self) -> Coordinate:
        return self._drawing_group_on_screen.top_left

    def cut(self, area: RectangleAreaOnScreen) -> Self:
        res: list[RelativeDrawing] = []
        for relative in self.relative_drawings:
            top_left = area.top_left - relative.top_left(ORIGIN)
            relative_area = top_left.anchor(area.size).rectangle_area_on_screen
            drawing = relative.drawing.cut(relative_area)
            relative_drawing = replace(relative, drawing=drawing)
            res.append(relative_drawing)
        return replace(self, relative_drawings=tuple(res))

    @cached_property
    def _drawing_group_on_screen(self) -> DrawingGroupOnScreen:
        from nextrpg.draw.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(ORIGIN, self)
