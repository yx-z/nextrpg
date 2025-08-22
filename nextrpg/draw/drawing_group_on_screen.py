from __future__ import annotations

from collections.abc import Hashable
from dataclasses import dataclass, replace
from functools import cached_property

from nextrpg.core.color import Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.polygon_on_screen import PolygonOnScreen
from nextrpg.draw.sizable_draw_on_screens import SizableDrawOnScreens
from nextrpg.global_config.global_config import config


@dataclass(frozen=True)
class DrawingGroupOnScreen(Sizable):
    origin: Coordinate
    drawing_group: DrawingGroup

    def add_tag(self, tag: Hashable) -> DrawingGroupOnScreen:
        drawing_group = self.drawing_group.add_tag(tag)
        return replace(self, drawing_group=drawing_group)

    @property
    def tags(self) -> tuple[Hashable, ...]:
        return self.drawing_group.tags

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    @cached_property
    def drawing_on_screens(self) -> list[DrawingOnScreen]:
        return self.get_drawing_on_screens(include_link_lines=True)

    def get_drawing_on_screens(
        self, include_link_lines: bool
    ) -> list[DrawingOnScreen]:
        res: list[DrawingOnScreen] = []
        for relative in self.drawing_group.relative_drawings:
            top_left = relative.top_left(self.origin)
            match relative.drawing:
                case DrawingGroup() as drawing_group:
                    res += drawing_group.drawing_on_screens(
                        top_left, include_link_lines
                    )
                case Drawing() as drawing:
                    drawing_on_screen = drawing.drawing_on_screen(top_left)
                    res.append(drawing_on_screen)
            if self._link_color and include_link_lines:
                declared_coord = self.origin + relative.shift
                points = (self.origin, declared_coord)
                link = PolygonOnScreen(points, closed=False)
                link_drawing_on_screen = link.line(self._link_color)
                res.append(link_drawing_on_screen)
        return res

    @cached_property
    def _sized(self) -> SizableDrawOnScreens:
        return SizableDrawOnScreens(self.drawing_on_screens)

    @cached_property
    def _link_color(self) -> Color | None:
        if (debug := config().debug) and debug.draw_group_link_color:
            return debug.draw_group_link_color
        return None
