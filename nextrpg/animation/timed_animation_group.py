from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Any, Self, TypeVar, override

from nextrpg.animation.animation_group import AnimationGroup
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.drawing.relative_animation_like import RelativeAnimationLike

_T = TypeVar("_T", bound="TimedAnimationGroup")


@dataclass_with_default(frozen=True)
class TimedAnimationGroup(AnimationGroup):
    duration: Millisecond
    _: KW_ONLY = private_init_below()
    _timer: Timer = default(lambda self: Timer(self.duration))

    def compose(self, other: type[_T], **kwargs: Any) -> _T:
        return other(resource=self.no_shift, duration=self.duration, **kwargs)

    @cached_property
    def reverse(self) -> Self:
        resource = tuple(_reverse(r) for r in self.resources)
        return replace(self, resource=resource, _timer=self._timer.countdown)

    @override
    @cached_property
    def is_complete(self) -> bool:
        return super().is_complete and self._timer.is_complete

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        ticked = super()._tick_before_complete(time_delta)
        timer = self._timer.tick(time_delta)
        return replace(ticked, _timer=timer)


def _reverse(resource: RelativeAnimationLike) -> RelativeAnimationLike:
    if isinstance(drawing := resource.resource, TimedAnimationGroup):
        return replace(resource, drawing=drawing.reverse)
    return resource
