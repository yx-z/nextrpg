from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation_group import AnimationGroup
from nextrpg.core.dataclass_with_default import default, private_init_below
from nextrpg.core.time import Millisecond, Timer
from nextrpg.drawing.animation_like import AnimationLike


@dataclass(frozen=True)
class TimedAnimationGroup(AnimationGroup):
    duration: Millisecond
    _: KW_ONLY = private_init_below()
    _timer: Timer = default(lambda self: Timer(self.duration))

    @cached_property
    def reverse(self) -> Self:
        if isinstance(self.resource, tuple):
            resource = tuple(_reverse(r) for r in self.resource)
        else:
            resource = _reverse(self.resource)
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


def _reverse(resource: AnimationLike) -> AnimationLike:
    if isinstance(resource, TimedAnimationGroup):
        return resource.reverse
    return resource
