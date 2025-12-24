from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.config.config import config
from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import Color
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.geometry.size import ZERO_SIZE


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
    def drawing_on_screens(self) -> DrawingOnScreens:
        res: list[DrawingOnScreen] = []
        for shifted in self.drawing_group.resources:
            res += shifted.drawing_on_screens(self.origin)
            if self._link_color and shifted.offset_size != ZERO_SIZE:
                declared_coordinate = self.origin + shifted.offset_size
                link = PolylineOnScreen((self.origin, declared_coordinate))
                link_drawing_on_screen = link.fill(
                    self._link_color, allow_background_in_debug=False
                )
                res.append(link_drawing_on_screen)
        return DrawingOnScreens(tuple(res))

    @cached_property
    def _link_color(self) -> Color | None:
        if (debug := config().debug) and debug.drawing_group_link:
            return debug.drawing_group_link
        return None
