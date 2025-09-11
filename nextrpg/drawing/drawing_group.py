from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self

from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.relative_drawing import RelativeDrawing
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import ZERO_SIZE, Size
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen


@dataclass(frozen=True)
class DrawingGroup(AnimationLike):
    relative_drawings: tuple[RelativeDrawing, ...]

    @property
    def drawing(self) -> DrawingGroup:
        return self

    @property
    def no_shift(self) -> RelativeDrawing:
        return self.shift(ZERO_SIZE)

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
        return self.group_on_screen(origin).drawing_on_screens

    def group_on_screen(self, origin: Coordinate) -> DrawingGroupOnScreen:
        from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(origin, self)

    @property
    def size(self) -> Size:
        return self._drawing_group_on_screen.size

    @property
    def top_left(self) -> Coordinate:
        return self._drawing_group_on_screen.top_left

    def _flip(self, horizontal: bool, vertical: bool) -> Self:
        relative_drawings = tuple(
            relative_drawing.flip(horizontal, vertical)
            for relative_drawing in self.relative_drawings
        )
        return replace(self, relative_drawings=relative_drawings)

    def _cut(self, area: RectangleAreaOnScreen) -> Self:
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
        from nextrpg.drawing.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(ORIGIN, self)
