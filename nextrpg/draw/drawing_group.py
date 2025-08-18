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

    def group_on_screen(self, origin: Coordinate) -> DrawingGroupOnScreen:
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

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        res: list[DrawingOnScreen] = []
        for relative, shift in self.drawing_group.relative_drawings:
            coordinate = self.origin + shift
            match relative:
                case Drawing() as drawing:
                    res.append(drawing.drawing_on_screen(coordinate))
                case DrawingGroup() as drawing_group:
                    res += drawing_group.drawing_on_screens(coordinate)
        return tuple(res)

    def coordinate(self, arg: Drawing | DrawingGroup) -> Coordinate | None:
        if arg == self.drawing_group:
            return self.origin
        for relative, shift in self.drawing_group.relative_drawings:
            coordinate = self.origin + shift
            match relative:
                case Drawing() as drawing:
                    if arg == drawing:
                        return coordinate
                case DrawingGroup() as group:
                    if res := group.group_on_screen(coordinate).coordinate(arg):
                        return res
        return None

    @cached_property
    def _sized(self) -> SizedDrawOnScreens:
        return SizedDrawOnScreens(self.drawing_on_screens)
