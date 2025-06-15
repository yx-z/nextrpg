"""
Static frames, when played sequentially, become animated.
"""

from dataclasses import dataclass
from typing import NamedTuple

from nextrpg.common_types import Millisecond
from nextrpg.draw_on_screen import Drawing

type FrameIndex = int
"""The zero-based index to point to a frame in a list of frames."""


@dataclass(frozen=True)
class CyclicFrames:
    frames: list[Drawing]
    frame_duration: Millisecond
    _index: FrameIndex = 0
    _elapsed: Millisecond = 0

    @property
    def current_frame(self) -> Drawing:
        return self.frames[self._index]

    def peek(self, time_delta: Millisecond) -> Drawing:
        return self.frames[self._step(time_delta).index]

    def step(self, time_delta: Millisecond) -> "CyclicFrames":
        return CyclicFrames(
            self.frames, self.frame_duration, *self._step(time_delta)
        )

    def reset(self) -> "CyclicFrames":
        return CyclicFrames(self.frames, self.frame_duration)

    def _step(self, time_delta: Millisecond) -> "_Step":
        total_time = self._elapsed + time_delta
        frames_to_advance = total_time // self.frame_duration
        remaining_elapsed = total_time % self.frame_duration
        new_index = (self._index + frames_to_advance) % len(self.frames)
        return _Step(new_index, remaining_elapsed)


class _Step(NamedTuple):
    index: FrameIndex
    elapsed: Millisecond
