from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple, Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.draw import DrawOnScreen
from nextrpg import Draw


class DrawRelativeTo(NamedTuple):
    draw: Draw | Group
    relative_to: Size


@dataclass(frozen=True)
class Group:
    leader: Draw | Self
    followers: DrawRelativeTo | tuple[DrawRelativeTo, ...]

    def draw_on_screens(
        self, leader_coordinate: Coordinate
    ) -> tuple[DrawOnScreen, ...]:
        return GroupOnScreen(leader_coordinate, self).draw_on_screens

    def group_on_screen(self, leader_coordinate: Coordinate) -> GroupOnScreen:
        return GroupOnScreen(leader_coordinate, self)

    @cached_property
    def size(self) -> Size:
        draw_on_screens = GroupOnScreen(Coordinate(0, 0), self).draw_on_screens
        min_left, min_top = min(
            d.rectangle_on_screen.top_left for d in draw_on_screens
        )
        max_left, max_top = max(
            d.rectangle_on_screen.bottom_right for d in draw_on_screens
        )
        width = max_left - min_left
        height = max_top - min_top
        return Size(width, height)


@dataclass(frozen=True)
class GroupOnScreen:
    top_left: Coordinate
    group: Group

    def group_coordinate(self, group: Group) -> Coordinate:
        if coord := self._group(group, lambda c: c):
            return coord
        raise ValueError(f"Group {group} not found.")

    def group_draw_on_screens(self, group: Group) -> tuple[DrawOnScreen, ...]:
        if d := self._group(
            group, lambda c: GroupOnScreen(c, group).draw_on_screens
        ):
            return d
        raise ValueError(f"Group {group} not found.")

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        res: list[DrawOnScreen] = []
        if isinstance(l := self.group.leader, Draw):
            res.append(DrawOnScreen(self.top_left, l))
        else:
            res += GroupOnScreen(self.top_left, l).draw_on_screens

        for draw, relative_to in self._followers:
            coord = self.top_left + relative_to
            if isinstance(draw, Draw):
                res.append(DrawOnScreen(coord, draw))
            else:
                res += GroupOnScreen(coord, draw).draw_on_screens

        return tuple(res)

    @property
    def _followers(self) -> tuple[DrawRelativeTo, ...]:
        if isinstance(f := self.group.followers, DrawRelativeTo):
            return (f,)
        return f

    def _group[T](
        self, group: Group, action: Callable[[Coordinate], T | None]
    ) -> T | None:
        if group == self.group:
            return action(self.top_left)

        if isinstance(l := self.group.leader, Group):
            if l == group:
                return action(self.top_left)
            if res := GroupOnScreen(self.top_left, l)._group(group, action):
                return res

        for draw, relative_to in self._followers:
            coord = self.top_left + relative_to
            if isinstance(draw, Draw):
                continue
            if draw == group:
                return action(coord)
            if res := GroupOnScreen(coord, draw)._group(group, action):
                return res

        return None
