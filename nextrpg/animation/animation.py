from abc import ABC, abstractmethod
from typing import Self, override

from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup


class Animation(AnimationLike, ABC):
    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self.is_complete:
            return self
        return self._tick_before_complete(time_delta)

    @property
    @abstractmethod
    def drawing(self) -> Drawing | DrawingGroup: ...

    @abstractmethod
    def _tick_before_complete(self, time_delta: Millisecond) -> Self: ...
