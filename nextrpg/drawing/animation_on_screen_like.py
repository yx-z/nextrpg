from functools import cached_property
from typing import TYPE_CHECKING, Self

from nextrpg.core.time import Millisecond
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen


class AnimationOnScreenLike(Sizable):
    drawing_on_screens: tuple[DrawingOnScreen, ...]

    @property
    def drawing_on_screen(self) -> DrawingOnScreen: ...

    def tick(self, time_delta: Millisecond) -> Self:
        return self

    @property
    def is_complete(self) -> bool:
        return True

    @cached_property
    def visible_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        min_top = min(
            drawing_on_screen.visible_rectangle_area_on_screen.top
            for drawing_on_screen in self.drawing_on_screens
        )
        min_left = min(
            drawing_on_screen.visible_rectangle_area_on_screen.left
            for drawing_on_screen in self.drawing_on_screens
        )
        max_bottom = max(
            drawing_on_screen.visible_rectangle_area_on_screen.bottom
            for drawing_on_screen in self.drawing_on_screens
        )
        max_right = max(
            drawing_on_screen.visible_rectangle_area_on_screen.right
            for drawing_on_screen in self.drawing_on_screens
        )
        coordinate = min_left.pair(min_top)
        width = max_right - min_left
        height = max_bottom - min_top
        size = width * height
        return RectangleAreaOnScreen(coordinate, size)


def tick_optional(
    animation: AnimationOnScreenLike | None, time_delta: Millisecond
) -> AnimationOnScreenLike | None:
    if animation:
        return animation.tick(time_delta)
    return None
