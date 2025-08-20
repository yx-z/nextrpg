from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from nextrpg.core.color import Color
from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing import (
    Drawing,
)
from nextrpg.draw.drawing_on_screen import DrawingOnScreen, SizableDrawOnScreens
from nextrpg.draw.polygon import PolygonOnScreen
from nextrpg.global_config.global_config import config


class RelativeDrawing(NamedTuple):
    drawing: Drawing | DrawingGroup
    shift: Size


@dataclass(frozen=True)
class DrawingGroup(Sizable):
    relative_drawings: tuple[RelativeDrawing, ...]

    def drawing_on_screens(
        self, origin: Coordinate, include_link_lines: bool = True
    ) -> tuple[DrawingOnScreen, ...]:
        return DrawingGroupOnScreen(origin, self).get_drawing_on_screens(
            include_link_lines
        )

    def group_on_screen(self, origin: Coordinate) -> DrawingGroupOnScreen:
        return DrawingGroupOnScreen(origin, self)

    @cached_property
    def size(self) -> Size:
        return DrawingGroupOnScreen(ORIGIN, self).size

    @cached_property
    def top_left(self) -> Coordinate:
        return DrawingGroupOnScreen(ORIGIN, self).top_left


@dataclass(frozen=True)
class DrawingGroupOnScreen(Sizable):
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
        return self.get_drawing_on_screens(include_link_lines=True)

    def get_drawing_on_screens(
        self, include_link_lines: bool
    ) -> tuple[DrawingOnScreen, ...]:
        res: list[DrawingOnScreen] = []
        for relative, shift in self.drawing_group.relative_drawings:
            coordinate = self.origin + shift
            match relative:
                case Drawing() as drawing:
                    drawing_on_screen = drawing.drawing_on_screen(coordinate)
                    res.append(drawing_on_screen)
                case DrawingGroup() as drawing_group:
                    res += drawing_group.drawing_on_screens(coordinate)
            if (
                self._link_color
                and coordinate != self.origin
                and include_link_lines
            ):
                points = (self.origin, coordinate)
                link = PolygonOnScreen(points, closed=False)
                link_drawing_on_screen = link.line(self._link_color)
                res.append(link_drawing_on_screen)
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
    def _sized(self) -> SizableDrawOnScreens:
        return SizableDrawOnScreens(self.drawing_on_screens)

    @cached_property
    def _link_color(self) -> Color | None:
        if (debug := config().debug) and debug.draw_group_link_color:
            return debug.draw_group_link_color
        return None
