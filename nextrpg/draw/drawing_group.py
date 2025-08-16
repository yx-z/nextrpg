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
    relative_drawings: tuple[RelativeDrawing, ...]

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

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    def coordinate(self, drawing_group: DrawingGroup) -> Coordinate:
        if coordinate := self._coordinate(drawing_group):
            return coordinate
        raise ValueError(f"DrawingGroup {drawing_group} not found.")

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        res: list[DrawingOnScreen] = []
        for relative_drawing, shift in self.drawing_group.relative_drawings:
            coordinate = self.origin + shift
            match relative_drawing:
                case Drawing() as drawing:
                    res.append(drawing.drawing_on_screen(coordinate))
                case DrawingGroup() as drawing_group:
                    res += drawing_group.drawing_on_screens(coordinate)
        return tuple(res)

    def _coordinate(self, drawing_group: DrawingGroup) -> Coordinate | None:
        if drawing_group == self.drawing_group:
            return self.origin
        for relative_drawing, shift in self.drawing_group.relative_drawings:
            coordinate = self.origin + shift
            match relative_drawing:
                case Drawing():
                    continue
                case DrawingGroup() as group:
                    if group == drawing_group:
                        return coordinate
                    drawing_group_on_screen = group.drawing_group_on_screen(
                        coordinate
                    )
                    if res := drawing_group_on_screen._coordinate(
                        drawing_group
                    ):
                        return res
        return None

    @cached_property
    def _sized(self) -> SizedDrawOnScreens:
        return SizedDrawOnScreens(self.drawing_on_screens)
