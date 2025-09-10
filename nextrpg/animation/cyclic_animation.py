from dataclasses import KW_ONLY, replace
from typing import Self, override

from nextrpg.animation.animation import Animation
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup


@dataclass_with_default(frozen=True)
class CyclicAnimation(Animation):
    frames: tuple[Drawing | DrawingGroup, ...]
    duration_per_frame: Millisecond | tuple[Millisecond, ...]
    _: KW_ONLY = private_init_below()
    _index: int = 0
    _timer: Timer = default(lambda self: Timer(self._duration(0)))

    @property
    @override
    def drawing(self) -> Drawing | DrawingGroup:
        return self.frames[self._index]

    @property
    def is_complete(self) -> bool:
        return False

    @property
    def reset(self) -> Self:
        timer = Timer(self._duration(0))
        return replace(self, _index=0, _timer=timer)

    def _duration(self, index: int) -> Millisecond:
        if isinstance(self.duration_per_frame, tuple):
            return self.duration_per_frame[index]
        return self.duration_per_frame

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        if not (updated_timer := self._timer.tick(time_delta)).is_complete:
            return replace(self, _timer=updated_timer)
        current_index = self._index
        remaining_time = updated_timer.elapsed - updated_timer.duration
        while remaining_time > 0:
            current_index = (current_index + 1) % len(self.frames)
            current_frame_duration = (
                self.duration_per_frame[current_index]
                if isinstance(self.duration_per_frame, tuple)
                else self.duration_per_frame
            )
            if remaining_time < current_frame_duration:
                break
            remaining_time -= current_frame_duration
        current_frame_duration = self._duration(current_index)
        new_timer = Timer(current_frame_duration).tick(remaining_time)
        return replace(self, _index=current_index, _timer=new_timer)
