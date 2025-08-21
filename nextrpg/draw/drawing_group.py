from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.relative_drawing import RelativeDrawing

if TYPE_CHECKING:
    from nextrpg.draw.drawing_group_on_screen import DrawingGroupOnScreen


@dataclass(frozen=True)
class DrawingGroup(Sizable):
    relative_drawings: tuple[RelativeDrawing, ...]

    def drawing_on_screens(
        self, origin: Coordinate, include_link_lines: bool = True
    ) -> tuple[DrawingOnScreen, ...]:
        from nextrpg.draw.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(origin, self).get_drawing_on_screens(
            include_link_lines
        )

    def group_on_screen(self, origin: Coordinate) -> DrawingGroupOnScreen:
        from nextrpg.draw.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(origin, self)

    @property
    def size(self) -> Size:
        return self._drawing_group_on_screen.size

    @property
    def top_left(self) -> Coordinate:
        return self._drawing_group_on_screen.top_left

    @cached_property
    def _drawing_group_on_screen(self) -> DrawingGroupOnScreen:
        from nextrpg.draw.drawing_group_on_screen import DrawingGroupOnScreen

        return DrawingGroupOnScreen(ORIGIN, self)
