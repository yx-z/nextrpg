from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self

from nextrpg.config.config import config
from nextrpg.core import Millisecond, alpha_from_percentage
from nextrpg.draw.draw_on_screen import DrawOnScreen


@dataclass(frozen=True)
class Fade:
    resource: tuple[DrawOnScreen, ...]
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _elapsed: Millisecond = 0

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if self.complete:
            return self._complete
        if self._elapsed == 0:
            return self._start
        return self.resource

    def tick(self, time_delta: Millisecond) -> Self:
        if self.complete:
            return self
        elapsed = self._elapsed + time_delta
        alpha = alpha_from_percentage(self._percentage)
        resource = tuple(d.set_alpha(alpha) for d in self.resource)
        return replace(self, _elapsed=elapsed, resource=resource)

    @cached_property
    def complete(self) -> bool:
        return self._elapsed >= self.duration

    @cached_property
    def _start(self) -> tuple[DrawOnScreen, ...]:
        return ()

    @cached_property
    def _complete(self) -> tuple[DrawOnScreen, ...]:
        return ()

    @cached_property
    def _percentage(self) -> float:
        return 0
