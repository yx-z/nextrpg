from abc import ABC, abstractmethod
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.sizable import Sizable


class Animation(Sizable, ABC):
    def tick(self, time_delta: Millisecond) -> Self:
        if self.is_complete:
            return self
        return self.tick_before_complete(time_delta)

    @abstractmethod
    def tick_before_complete(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def drawing(self) -> Drawing | DrawingGroup: ...

    @property
    @abstractmethod
    def is_complete(self) -> bool: ...

    @property
    def top_left(self) -> Coordinate:
        return self.drawing.top_left

    @property
    def size(self) -> Size:
        return self.drawing.size
