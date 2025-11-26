from collections.abc import Iterable
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Protocol,
    Self,
    overload,
    runtime_checkable,
)

from pygame import Surface

from nextrpg.core.time import Millisecond
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.directional_offset import DirectionalOffset
from nextrpg.geometry.sizable import Sizable
from nextrpg.geometry.size import Height, Size, Width

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
    from nextrpg.game.game_state import GameState


@runtime_checkable
class SpriteOnScreen(Sizable, Protocol):
    drawing_on_screens: tuple[DrawingOnScreen, ...]

    @cached_property
    def pygame(self) -> tuple[Surface, Coordinate]:
        return self.drawing_on_screen.pygame

    def __add__(
        self, other: Coordinate | Width | Height | Size | DirectionalOffset
    ) -> SpriteOnScreen:
        return self._drawing_on_screens + other

    def __sub__(
        self, other: Coordinate | Width | Height | Size | DirectionalOffset
    ) -> SpriteOnScreen:
        return self._drawing_on_screens + -other

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
    resource: SpriteOnScreen | tuple[SpriteOnScreen, ...],
    animation: type[TimedAnimationGroup],
    anchor: Anchor = Anchor.TOP_LEFT,
    **kwargs: Any,
) -> TimedAnimationOnScreens: ...


@overload
def animate(
    resource: SpriteOnScreen | tuple[SpriteOnScreen, ...],
    animation: type[AnimationGroup],
    anchor: Anchor = Anchor.TOP_LEFT,
    **kwargs: Any,
) -> AnimationOnScreens: ...


def animate(
    resource: SpriteOnScreen | tuple[SpriteOnScreen, ...],
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


def tick_all_with_state[T](
    tickables: Iterable[T], time_delta: Millisecond, state: GameState
) -> tuple[T, GameState]:
    res: list[T] = []
    for tickable in tickables:
        ticked, state = tickable.tick(time_delta, state)
        res.append(ticked)
    all_ticked = tuple(res)
    return all_ticked, state
