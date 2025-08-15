from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from nextrpg.core.coordinate import ORIGIN, Coordinate, Moving
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.core.time import Millisecond
from nextrpg.draw.animation import Animation
from nextrpg.draw.drawing import Drawing, DrawingOnScreen, SizedDrawOnScreens


@dataclass(frozen=True)
class RelativeDrawing:
    drawing: Animation | Drawing | DrawingGroup
    shift: Size | Moving

    def __iter__(
        self,
    ) -> tuple[Animation | Drawing | DrawingGroup, Size | Moving]:
        return iter((self.drawing, self.shift))

    def tick(self, time_delta: Millisecond) -> Self:
        if isinstance(drawing := self.drawing, Animation | DrawingGroup):
            drawing = drawing.tick(time_delta)
        if isinstance(shift := self.shift, Moving):
            shift = shift.tick(time_delta)
        return replace(self, drawing=drawing, shift=shift)


@dataclass(frozen=True)
class DrawingGroup(Sizeable):
    relative_drawings: tuple[RelativeDrawing, ...]

    def tick(self, time_delta: Millisecond) -> Self:
        relative_drawings = tuple(
            relative_drawing.tick(time_delta)
            for relative_drawing in self.relative_drawings
        )
        return replace(self, relative_drawings=relative_drawings)

    def drawing_on_screens(
        self, origin: Coordinate
    ) -> tuple[DrawingOnScreen, ...]:
        return DrawingGroupOnScreen(origin, self).drawing_on_screens

    def drawing_group_on_screen(
        self, origin: Coordinate
    ) -> DrawingGroupOnScreen:
        return DrawingGroupOnScreen(origin, self)

    @cached_property
    def size(self) -> Size:
        return DrawingGroupOnScreen(ORIGIN, self).size

    @cached_property
    def top_left(self) -> Coordinate:
        return DrawingGroupOnScreen(ORIGIN, self).top_left


@dataclass(frozen=True)
class DrawingGroupOnScreen(Sizeable):
    origin: Coordinate
    drawing_group: DrawingGroup

    def tick(self, time_delta: Millisecond) -> Self:
        drawing_group = self.drawing_group.tick(time_delta)
        return replace(self, drawing_group=drawing_group)

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    def coordinate(self, drawing_group: DrawingGroup) -> Coordinate:
        if coord := self._coordinate(drawing_group):
            return coord
        raise ValueError(f"Group {drawing_group} not found.")

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        res: list[DrawingOnScreen] = []
        for drawing, shift in self.drawing_group.relative_drawings:
            coord = self.origin + shift
            if isinstance(drawing, Drawing):
                res.append(DrawingOnScreen(coord, drawing))
            else:
                res += DrawingGroupOnScreen(coord, drawing).drawing_on_screens

        return tuple(res)

    def _coordinate(self, drawing_group: DrawingGroup) -> Coordinate | None:
        if drawing_group == self.drawing_group:
            return self.origin
        for drawing, shift in self.drawing_group.relative_drawings:
            coord = self.origin + shift
            if isinstance(drawing, Drawing):
                continue
            if drawing == drawing_group:
                return coord
            if res := DrawingGroupOnScreen(coord, drawing)._coordinate(
                drawing_group
            ):
                return res
        return None

    @cached_property
    def _sized(self) -> SizedDrawOnScreens:
        return SizedDrawOnScreens(self.drawing_on_screens)
