from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.draw.drawing import Drawing, DrawingOnScreen, SizedDrawOnScreens


class RelativeDrawing(NamedTuple):
    drawing: Drawing | DrawingGroup
    shift: Size


@dataclass(frozen=True)
class DrawingGroup(Sizeable):
    drawing: tuple[RelativeDrawing, ...]

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

    @property
    def top_left(self) -> Coordinate:
        return DrawingGroupOnScreen(ORIGIN, self).top_left


@dataclass(frozen=True)
class DrawingGroupOnScreen:
    origin: Coordinate
    group: DrawingGroup

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    def coordinate(self, group: DrawingGroup) -> Coordinate:
        if coord := self._coordinate(group):
            return coord
        raise ValueError(f"Group {group} not found.")

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        res: list[DrawingOnScreen] = []
        for draw, shift in self.group.drawing:
            coord = self.origin + shift
            if isinstance(draw, Drawing):
                res.append(DrawingOnScreen(coord, draw))
            else:
                res += DrawingGroupOnScreen(coord, draw).drawing_on_screens

        return tuple(res)

    def _coordinate(self, group: DrawingGroup) -> Coordinate | None:
        if group == self.group:
            return self.origin
        for drawing, shift in self.group.drawing:
            coord = self.origin + shift
            if isinstance(drawing, Drawing):
                continue
            if drawing == group:
                return coord
            if res := DrawingGroupOnScreen(coord, drawing)._coordinate(group):
                return res
        return None

    @cached_property
    def _sized(self) -> SizedDrawOnScreens:
        return SizedDrawOnScreens(self.drawing_on_screens)
