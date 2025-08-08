from dataclasses import KW_ONLY, dataclass, replace
from typing import Self

from pygame.time import get_ticks

from nextrpg.core.dataclass_with_init import not_constructor_below

type Millisecond = int


@dataclass(frozen=True)
class Timer:
    duration: Millisecond
    _: KW_ONLY = not_constructor_below()
    elapsed: Millisecond = 0

    @property
    def modulo(self) -> Self:
        return self.reset.tick(self.elapsed % self.duration)

    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, elapsed=self.elapsed + time_delta)

    @property
    def reset(self) -> Self:
        return replace(self, elapsed=0)

    @property
    def complete(self) -> bool:
        return self.elapsed > self.duration

    @property
    def completed_percentage(self) -> float:
        return self.elapsed / self.duration

    @property
    def remaining(self) -> Millisecond:
        return self.duration - self.elapsed

    @property
    def remaining_percentage(self) -> float:
        return self.remaining / self.duration


def get_timepoint() -> Millisecond:
    return get_ticks()
