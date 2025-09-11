from abc import ABC, abstractmethod
from typing import Self, override

from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size


class Animation(AnimationLike, ABC):
    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self.is_complete:
            return self
        return self._tick_before_complete(time_delta)

    @property
    def top_left(self) -> Coordinate:
        return self.drawing.top_left

    @property
    def size(self) -> Size:
        return self.drawing.size

    @override
    @property
    @abstractmethod
    def is_complete(self) -> bool: ...

    @property
    @abstractmethod
    def drawing(self) -> Drawing | DrawingGroup: ...

    @override
    @property
    def drawings(self) -> tuple[Drawing, ...]:
        return self.drawing.drawings

    @abstractmethod
    def _tick_before_complete(self, time_delta: Millisecond) -> Self: ...
