from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.config.config import config
from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import Color
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import ZERO_SIZE
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen


@dataclass(frozen=True)
class DrawingGroupOnScreen(SpriteOnScreen):
    origin: Coordinate
    drawing_group: DrawingGroup

    @override
    @cached_property
    def is_complete(self) -> bool:
        return self.drawing_group.is_complete

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        drawing_group = self.drawing_group.tick(time_delta)
        return replace(self, drawing_group=drawing_group)

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        res: list[DrawingOnScreen] = []
        for relative in self.drawing_group.resources:
            res += relative.drawing_on_screens(self.origin)
            if self._link_color and relative.shift != ZERO_SIZE:
                declared_coord = self.origin + relative.shift
                points = (self.origin, declared_coord)
                link = PolylineOnScreen(points)
                link_drawing_on_screen = link.fill(
                    self._link_color, allow_background_in_debug=False
                )
                res.append(link_drawing_on_screen)
        return tuple(res)

    @cached_property
    def _link_color(self) -> Color | None:
        if (debug := config().debug) and debug.draw_group_link_color:
            return debug.draw_group_link_color
        return None
