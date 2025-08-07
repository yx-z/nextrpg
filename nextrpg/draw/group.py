from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from nextrpg.core.coordinate import Coordinate, ORIGIN
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.draw.draw import Draw, DrawOnScreen, SizedDrawOnScreens


class RelativeDraw(NamedTuple):
    draw: Draw | Group
    shift: Size


@dataclass(frozen=True)
class Group(Sizeable):
    draw: RelativeDraw | tuple[RelativeDraw, ...]

    @property
    def draws(self) -> tuple[RelativeDraw, ...]:
        if isinstance(self.draw, RelativeDraw):
            return (self.draw,)
        return self.draw

    def draw_on_screens(self, origin: Coordinate) -> tuple[DrawOnScreen, ...]:
        return GroupOnScreen(origin, self).draw_on_screens

    def group_on_screen(self, origin: Coordinate) -> GroupOnScreen:
        return GroupOnScreen(origin, self)

    @cached_property
    def size(self) -> Size:
        return GroupOnScreen(ORIGIN, self).size

    @property
    def top_left(self) -> Coordinate:
        return GroupOnScreen(ORIGIN, self).top_left


@dataclass(frozen=True)
class GroupOnScreen:
    origin: Coordinate
    group: Group

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    def coordinate(self, group: Group) -> Coordinate:
        if coord := self._coordinate(group):
            return coord
        raise ValueError(f"Group {group} not found.")

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        res: list[DrawOnScreen] = []
        for draw, shift in self.group.draws:
            coord = self.origin + shift
            if isinstance(draw, Draw):
                res.append(DrawOnScreen(coord, draw))
            else:
                res += GroupOnScreen(coord, draw).draw_on_screens

        return tuple(res)

    def _coordinate(self, group: Group) -> Coordinate | None:
        if group == self.group:
            return self.origin
        for draw, shift in self.group.draws:
            coord = self.origin + shift
            if isinstance(draw, Draw):
                continue
            if draw == group:
                return coord
            if res := GroupOnScreen(coord, draw)._coordinate(group):
                return res
        return None

    @cached_property
    def _sized(self) -> SizedDrawOnScreens:
        return SizedDrawOnScreens(self.draw_on_screens)
