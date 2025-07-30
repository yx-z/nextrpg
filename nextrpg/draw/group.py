from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.draw import Draw, DrawOnScreen


class RelativeDraw(NamedTuple):
    draw: Draw | Group
    shift: Size


@dataclass(frozen=True)
class Group:
    draw: RelativeDraw | tuple[RelativeDraw, ...]

    @cached_property
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
        draw_on_screens = GroupOnScreen(Coordinate(0, 0), self).draw_on_screens
        min_left = min(d.top_left.left for d in draw_on_screens)
        min_top = min(d.top_left.top for d in draw_on_screens)
        max_left = max(
            d.rectangle_on_screen.bottom_right.left for d in draw_on_screens
        )
        max_top = max(
            d.rectangle_on_screen.bottom_right.top for d in draw_on_screens
        )
        width = max_left - min_left
        height = max_top - min_top
        return Size(width, height)


@dataclass(frozen=True)
class GroupOnScreen:
    top_left: Coordinate
    group: Group

    def coordinate(self, group: Group) -> Coordinate:
        if coord := self._coordinate(group):
            return coord
        raise ValueError(f"Group {group} not found.")

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        res: list[DrawOnScreen] = []
        for draw, shift in self.group.draws:
            coord = self.top_left + shift
            if isinstance(draw, Draw):
                res.append(DrawOnScreen(coord, draw))
            else:
                res += GroupOnScreen(coord, draw).draw_on_screens

        return tuple(res)

    def _coordinate(self, group: Group) -> Coordinate | None:
        if group == self.group:
            return self.top_left
        for draw, shift in self.group.draws:
            coord = self.top_left + shift
            if isinstance(draw, Draw):
                continue
            if draw == group:
                return coord
            if res := GroupOnScreen(coord, draw)._coordinate(group):
                return res
        return None
