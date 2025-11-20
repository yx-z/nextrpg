from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
    Self,
    overload,
    runtime_checkable,
)

from nextrpg.core.time import Millisecond
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.animation.animation_group import AnimationGroup
    from nextrpg.animation.animation_on_screen import AnimationOnScreen
    from nextrpg.animation.animation_on_screens import AnimationOnScreens
    from nextrpg.animation.timed_animation_group import TimedAnimationGroup
    from nextrpg.animation.timed_animation_on_screen import (
        TimedAnimationOnScreen,
    )
    from nextrpg.animation.timed_animation_on_screens import (
        TimedAnimationOnScreens,
    )
    from nextrpg.drawing.drawing_group import DrawingGroup
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.drawing.drawing_on_screens import DrawingOnScreens


@runtime_checkable
class SpriteOnScreen(Sizable, Protocol):
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

    @overload
    def animate(
        self,
        animation_type: type[TimedAnimationGroup],
        anchor: Anchor = Anchor.TOP_LEFT,
        **kwargs: Any,
    ) -> TimedAnimationOnScreen: ...

    @overload
    def animate(
        self,
        animation_type: type[AnimationGroup],
        anchor: Anchor = Anchor.TOP_LEFT,
        **kwargs: Any,
    ) -> AnimationOnScreen: ...

    def animate(
        self,
        animation_type: type[AnimationGroup] | type[TimedAnimationGroup],
        anchor: Anchor = Anchor.TOP_LEFT,
        **kwargs: Any,
    ) -> AnimationOnScreen | TimedAnimationOnScreen:
        from nextrpg.animation.animation_on_screen import AnimationOnScreen
        from nextrpg.animation.timed_animation_group import TimedAnimationGroup
        from nextrpg.animation.timed_animation_on_screen import (
            TimedAnimationOnScreen,
        )

        origin = self._drawing_on_screens.at_anchor(anchor)
        resource = tuple(
            drawing_on_screen.drawing.shift(
                drawing_on_screen.at_anchor(anchor) - origin,
                anchor,
            )
            for drawing_on_screen in self.drawing_on_screens
        )
        animation_group = animation_type(resource, **kwargs)
        if isinstance(animation_group, TimedAnimationGroup):
            return TimedAnimationOnScreen(origin, animation_group)
        return AnimationOnScreen(origin, animation_group)

    @cached_property
    def drawing_group_at_origin(self) -> DrawingGroup:
        from nextrpg.drawing.drawing_group import DrawingGroup

        sprites = tuple(
            drawing_on_screen.drawing
            + (drawing_on_screen.top_left - self._drawing_on_screens.top_left)
            for drawing_on_screen in self.drawing_on_screens
        )
        return DrawingGroup(sprites)

    @cached_property
    def _drawing_on_screens(self) -> DrawingOnScreens:
        from nextrpg.drawing.drawing_on_screens import DrawingOnScreens

        return DrawingOnScreens(self.drawing_on_screens)


@overload
def animate(
    resource: SpriteOnScreen | list[SpriteOnScreen],
    animation: type[TimedAnimationGroup],
    anchor: Anchor = Anchor.TOP_LEFT,
    **kwargs: Any,
) -> TimedAnimationOnScreens: ...


@overload
def animate(
    resource: SpriteOnScreen | list[SpriteOnScreen],
    animation: type[AnimationGroup],
    anchor: Anchor = Anchor.TOP_LEFT,
    **kwargs: Any,
) -> AnimationOnScreens: ...


def animate(
    resource: SpriteOnScreen | list[SpriteOnScreen],
    animation_type: type[TimedAnimationGroup] | type[AnimationGroup],
    anchor: Anchor = Anchor.TOP_LEFT,
    **kwargs: Any,
) -> AnimationOnScreens | TimedAnimationOnScreens:
    from nextrpg.animation.animation_on_screens import AnimationOnScreens
    from nextrpg.animation.timed_animation_group import TimedAnimationGroup
    from nextrpg.animation.timed_animation_on_screens import (
        TimedAnimationOnScreens,
    )

    if isinstance(resource, SpriteOnScreen):
        resources = resource.animate(animation_type, anchor, **kwargs)
    else:
        resources = tuple(
            res.animate(animation_type, anchor, **kwargs) for res in resource
        )

    if issubclass(animation_type, TimedAnimationGroup):
        return TimedAnimationOnScreens(resources)
    return AnimationOnScreens(resources)
