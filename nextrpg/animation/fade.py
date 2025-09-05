from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.color import alpha_from_percentage
from nextrpg.draw.drawing_on_screen import DrawingOnScreen


@dataclass_with_default(frozen=True)
class Fade(AnimationOnScreens, ABC):
    duration: Millisecond = field(
        default_factory=lambda: config().timing.fade_duration
    )
    _: KW_ONLY = private_init_below()
    _timer: Timer = default(lambda self: Timer(self.duration))

    @cached_property
    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self._timer.overdue:
            return self._end
        if not self._timer.started:
            return self._start

        alpha = alpha_from_percentage(self._percentage)
        return tuple(d.set_alpha(alpha) for d in super().drawing_on_screens)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        resource_ticked = super().tick(time_delta)
        timer = self._timer.tick(time_delta)
        return replace(resource_ticked, _timer=timer)

    @override
    @property
    def complete(self) -> bool:
        return self._timer.overdue

    @property
    @abstractmethod
    def _start(self) -> tuple[DrawingOnScreen, ...]: ...

    @property
    @abstractmethod
    def _end(self) -> tuple[DrawingOnScreen, ...]: ...

    @property
    @abstractmethod
    def _percentage(self) -> float: ...


@dataclass(frozen=True)
class FadeIn(Fade):
    final_alpha_percentage: float = 1.0

    @override
    @property
    def _start(self) -> tuple[DrawingOnScreen, ...]:
        return ()

    @override
    @property
    def _end(self) -> tuple[DrawingOnScreen, ...]:
        return super(Fade, self).drawing_on_screens

    @override
    @cached_property
    def _percentage(self) -> float:
        return self._timer.completed_percentage * self.final_alpha_percentage


@dataclass(frozen=True)
class FadeOut(Fade):
    final_alpha_percentage: float = 0.0

    @override
    @cached_property
    def _percentage(self) -> float:
        return self._timer.remaining_percentage * (
            1 - self.final_alpha_percentage
        )

    @override
    @property
    def _start(self) -> tuple[DrawingOnScreen, ...]:
        return super(Fade, self).drawing_on_screens

    @override
    @property
    def _end(self) -> tuple[DrawingOnScreen, ...]:
        return ()
