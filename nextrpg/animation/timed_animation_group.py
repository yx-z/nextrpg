from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Any, Self, override

from nextrpg.animation.animation_group import AnimationGroup
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.drawing.shifted_sprite import ShiftedSprite


@dataclass_with_default(frozen=True)
class TimedAnimationGroup(AnimationGroup):
    duration: Millisecond = field(
        default_factory=lambda: config().animation.default_timed_animation_duration
    )
    _: KW_ONLY = private_init_below()
    _timer: Timer = default(lambda self: Timer(self.duration))

    def compose[T: TimedAnimationGroup](
        self, other: type[T], **kwargs: Any
    ) -> T:
        return other(resource=self, duration=self.duration, **kwargs)

    @cached_property
    def reversed(self) -> Self:
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


def _reverse(resource: ShiftedSprite) -> ShiftedSprite:
    if isinstance(drawing := resource.resource, TimedAnimationGroup):
        return replace(resource, resource=drawing.reversed)
    return resource
