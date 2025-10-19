from abc import ABC, abstractmethod
from typing import override

from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup


class AbstractAnimation(AnimationLike, ABC):
    @override
    def tick(self, time_delta: Millisecond) -> AnimationLike:
        if self.is_complete:
            return self
        return self._tick_before_complete(time_delta)

    @override
    @property
    @abstractmethod
    def is_complete(self) -> bool: ...

    @property
    @abstractmethod
    def drawing(self) -> Drawing | DrawingGroup: ...

    @abstractmethod
    def _tick_before_complete(
        self, time_delta: Millisecond
    ) -> AnimationLike: ...
