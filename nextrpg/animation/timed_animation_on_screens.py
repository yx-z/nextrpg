from dataclasses import KW_ONLY, replace
from typing import Self, override

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer


@dataclass_with_default(frozen=True)
class TimedAnimationOnScreens(AnimationOnScreens):
    duration: Millisecond
    _: KW_ONLY = private_init_below()
    _timer: Timer = default(lambda self: Timer(self.duration))

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        ticked = super()._tick_before_complete(time_delta)
        timer = self._timer.tick(time_delta)
        return replace(ticked, _timer=timer)

    @override
    @property
    def is_complete(self) -> bool:
        return super().is_complete and self._timer.is_complete
