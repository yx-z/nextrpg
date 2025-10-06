from dataclasses import KW_ONLY, replace
from typing import Any, Self, override

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike


@dataclass_with_default(frozen=True)
class TimedAnimationOnScreens(AnimationOnScreens):
    duration: Millisecond
    _: KW_ONLY = private_init_below()
    _timer: Timer = default(lambda self: Timer(self.duration))

    def compose(
        self, other: type[TimedAnimationOnScreens], **kwargs: Any
    ) -> TimedAnimationOnScreens:
        return other(resource=self, duration=self.duration, **kwargs)

    @property
    def reverse(self) -> Self:
        if isinstance(self.resource, tuple):
            resource = tuple(_reverse(r) for r in self.resource)
        else:
            resource = _reverse(self.resource)
        return replace(self, resource=resource, _timer=self._timer.countdown)

    @override
    @property
    def is_complete(self) -> bool:
        return super().is_complete and self._timer.is_complete

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        ticked = super()._tick_before_complete(time_delta)
        timer = self._timer.tick(time_delta)
        return replace(ticked, _timer=timer)


def _reverse(resource: AnimationOnScreenLike) -> AnimationOnScreenLike:
    if isinstance(resource, TimedAnimationOnScreens):
        return resource.reverse
    return resource
