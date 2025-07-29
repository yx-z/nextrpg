from dataclasses import KW_ONLY, replace
from typing import Self, override

from nextrpg.draw.draw import Draw
from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.animated import Animated


@dataclass_with_instance_init(frozen=True)
class CyclicFrames(Animated):
    frames: tuple[Draw, ...]
    duration_per_frame: Millisecond
    _: KW_ONLY = not_constructor_below()
    _index: int = 0
    _timer: Timer = instance_init(lambda self: Timer(self.duration_per_frame))

    @property
    @override
    def draw(self) -> Draw:
        return self.frames[self._index]

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        timer = self._timer.tick(time_delta)
        frames_to_step = timer.elapsed // self.duration_per_frame
        index = (self._index + frames_to_step) % len(self.frames)
        return replace(self, _index=index, _timer=timer.modulo)

    @property
    def reset(self) -> Self:
        return replace(self, _index=0, _timer=self._timer.reset)
