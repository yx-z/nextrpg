"""
Static frames, when played sequentially, become animated.
"""

from dataclasses import dataclass, replace
from functools import cached_property

from nextrpg.common_types import Millisecond
from nextrpg.draw_on_screen import Drawing


@dataclass(frozen=True)
class CyclicFrames:
    frames: list[Drawing]
    duration_per_frame: Millisecond
    _index: int = 0
    _elapsed: Millisecond = 0

    @cached_property
    def current_frame(self) -> Drawing:
        return self.frames[self._index]

    def step(self, time_delta: Millisecond) -> "CyclicFrames":
        total_time = self._elapsed + time_delta
        frames_to_step = total_time // self.duration_per_frame
        return replace(
            self,
            _index=(self._index + frames_to_step) % len(self.frames),
            _elapsed=total_time % self.duration_per_frame,
        )

    def reset(self) -> "CyclicFrames":
        return replace(self, _index=0, _elapsed=0)
