from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple, Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg import Draw


class DrawRelativeTo(NamedTuple):
    drawing: Draw | DrawingGroup
    relative_to: Size


@dataclass(frozen=True)
class DrawingGroup:
    leader: Draw | Self
    followers: tuple[DrawRelativeTo, ...]

    def draw_on_screens(
        self, leader_coordinate: Coordinate
    ) -> tuple[DrawOnScreen, ...]:
        return DrawingGroupOnScreen(leader_coordinate, self).draw_on_screens

    def drawing_group_on_screen(
        self, leader_coordinate: Coordinate
    ) -> DrawingGroupOnScreen:
        return DrawingGroupOnScreen(leader_coordinate, self)

    @cached_property
    def size(self) -> Size:
        draw_on_screens = self.draw_on_screens(Coordinate(0, 0))
        min_left, min_top = min(d.top_left for d in draw_on_screens)
        max_left, max_top = max(
            d.rectangle.bottom_right for d in draw_on_screens
        )
        width = max_left - min_left
        height = max_top - min_top
        return Size(width, height)


@dataclass(frozen=True)
class DrawingGroupOnScreen:
    top_left: Coordinate
    group: DrawingGroup

    def draw_on_screen_group(
        self, group: DrawingGroup
    ) -> tuple[DrawOnScreen, ...]:
        if group == self.group:
            return self.draw_on_screens

        if isinstance(l := self.group.leader, DrawingGroup):
            if l == group:
                return DrawingGroupOnScreen(
                    self.top_left, group
                ).draw_on_screens
            if res := DrawingGroupOnScreen(
                self.top_left, l
            ).draw_on_screen_group(group):
                return res

        for draw, relative_to in self.group.followers:
            coord = self.top_left + relative_to
            if isinstance(draw, Draw):
                continue
            if draw == group:
                return DrawingGroupOnScreen(coord, group).draw_on_screens
            if res := DrawingGroupOnScreen(coord, draw).draw_on_screen_group(
                group
            ):
                return res

        return ()

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        res: list[DrawOnScreen] = []
        if isinstance(l := self.group.leader, Draw):
            res.append(DrawOnScreen(self.top_left, l))
        else:
            res += DrawingGroupOnScreen(self.top_left, l).draw_on_screens

        for draw, relative_to in self.group.followers:
            coord = self.top_left + relative_to
            if isinstance(draw, Draw):
                res.append(DrawOnScreen(coord, draw))
            else:
                res += DrawingGroupOnScreen(coord, draw).draw_on_screens

        return tuple(res)
