from functools import cached_property
from typing import TYPE_CHECKING, Any, Self, TypeVar

from nextrpg.core.time import Millisecond
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.animation.animation_group import AnimationGroup
    from nextrpg.animation.animation_on_screen import AnimationOnScreen
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.drawing.drawing_on_screens import DrawingOnScreens

    _T = TypeVar("_T", bound=AnimationGroup)


class AnimationOnScreenLike(Sizable):
    drawing_on_screens: tuple[DrawingOnScreen, ...]

    @cached_property
    def drawing_on_screen(self) -> DrawingOnScreen:
        return self._drawing_on_screens.drawing_on_screen

    @cached_property
    def top_left(self) -> Coordinate:
        return self._drawing_on_screens.top_left

    @cached_property
    def size(self) -> Size:
        return self._drawing_on_screens.size

    def tick(self, time_delta: Millisecond) -> Self:
        return self

    @cached_property
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
        coordinate = min_left @ min_top
        width = max_right - min_left
        height = max_bottom - min_top
        size = width * height
        return RectangleAreaOnScreen(coordinate, size)

    def animate(self, animation: type[_T], **kwargs: Any) -> AnimationOnScreen:
        from nextrpg.animation.animation_on_screen import AnimationOnScreen

        resource = tuple(
            drawing_on_screen.drawing.shift(drawing_on_screen.top_left.size)
            for drawing_on_screen in self.drawing_on_screens
        )
        return AnimationOnScreen(ORIGIN, animation(resource, **kwargs))

    @cached_property
    def _drawing_on_screens(self) -> DrawingOnScreens:
        from nextrpg.drawing.drawing_on_screens import DrawingOnScreens

        return DrawingOnScreens(self.drawing_on_screens)


def tick_optional(
    animation: AnimationOnScreenLike | None,
    time_delta: Millisecond,
) -> AnimationOnScreenLike | None:
    if animation:
        return animation.tick(time_delta)
    return None


def animate(
    resource: AnimationOnScreenLike | tuple[AnimationOnScreenLike, ...],
    animation: type[_T],
    **kwargs: Any
) -> AnimationOnScreenLike:
    from nextrpg.animation.animation_on_screens import AnimationOnScreens

    if isinstance(resource, tuple):
        animations = tuple(res.animate(animation, **kwargs) for res in resource)
        return AnimationOnScreens(animations)
    return resource.animate(animation, **kwargs)
