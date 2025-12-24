from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Self, override

import pygame

from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.util import Percentage

type Millisecond = int


@dataclass(frozen=True)
class Timer:
    duration: Millisecond
    _: KW_ONLY = private_init_below()
    elapsed: Millisecond = 0

    @cached_property
    def countdown(self) -> Countdown:
        return Countdown(self.duration)

    @cached_property
    def modulo(self) -> Self:
        return self.reset.tick(self.elapsed % self.duration)

    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, elapsed=self.elapsed + time_delta)

    @cached_property
    def reset(self) -> Self:
        return replace(self, elapsed=0)

    @cached_property
    def is_complete(self) -> bool:
        return self.elapsed >= self.duration

    @cached_property
    def completed_percentage(self) -> Percentage:
        return self.elapsed / self.duration

    @cached_property
    def remaining(self) -> Millisecond:
        return self.duration - self.elapsed

    @cached_property
    def remaining_percentage(self) -> Percentage:
        return self.remaining / self.duration


@dataclass_with_default(frozen=True)
class Countdown(Timer):
    _: KW_ONLY = private_init_below()
    elapsed: Millisecond = default(lambda self: self.duration)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        elapsed = max(self.elapsed - time_delta, 0)
        return replace(self, elapsed=elapsed)

    @override
    @cached_property
    def reset(self) -> Self:
        return replace(self, elapsed=self.duration)

    @override
    @cached_property
    def is_complete(self) -> bool:
        return self.elapsed <= 0


def get_timepoint() -> Millisecond:
    return pygame.time.get_ticks()
