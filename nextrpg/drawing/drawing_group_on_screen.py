from dataclasses import dataclass
from functools import cached_property
from typing import Self

from nextrpg.config.config import config
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.color import Color
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen


@dataclass(frozen=True)
class DrawingGroupOnScreen(AnimationOnScreenLike):
    origin: Coordinate
    drawing_group: DrawingGroup

    @property
    def size(self) -> Size:
        return self._drawing_on_screens.size

    @property
    def top_left(self) -> Coordinate:
        return self._drawing_on_screens.top_left

    def tick(self, time_delta: Millisecond) -> Self:
        return self

    @property
    def is_complete(self) -> bool:
        return True

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        res: list[DrawingOnScreen] = []
        for relative in self.drawing_group.relative_drawings:
            top_left = relative.top_left(self.origin)
            match relative.drawing:
                case DrawingGroup() as drawing_group:
                    res += drawing_group.drawing_on_screens(top_left)
                case Drawing() as drawing:
                    drawing_on_screen = drawing.drawing_on_screen(top_left)
                    res.append(drawing_on_screen)

            declared_coord = self.origin + relative.shift
            if self._link_color and self.origin != declared_coord:
                points = (self.origin, declared_coord)
                link = PolylineOnScreen(points)
                link_drawing_on_screen = link.fill(self._link_color)
                res.append(link_drawing_on_screen)
        return tuple(res)

    @cached_property
    def _drawing_on_screens(self) -> DrawingOnScreens:
        return DrawingOnScreens(self.drawing_on_screens)

    @cached_property
    def _link_color(self) -> Color | None:
        if (debug := config().debug) and debug.draw_group_link_color:
            return debug.draw_group_link_color
        return None
