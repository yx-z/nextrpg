from dataclasses import dataclass, replace
from typing import Self

from nextrpg.core.time import Millisecond, Percentage


@dataclass(frozen=True)
class AudioConfig:
    volume: Percentage = 1.0
    fade_in_duration: Millisecond = 0
    fade_out_duration: Millisecond = 0

    def with_volume(self, volume: Percentage) -> Self:
        return replace(self, volume=volume)

    def with_fade_in(self, duration: Millisecond) -> Self:
        return replace(self, fade_in_duration=duration)

    def with_fade_out(self, duration: Millisecond) -> Self:
        return replace(self, fade_out_duration=duration)
