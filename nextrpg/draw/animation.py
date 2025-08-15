from abc import ABC, abstractmethod
from typing import Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup


class Animation(Sizeable, ABC):
    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def drawing(self) -> Drawing | DrawingGroup: ...

    @property
    def top_left(self) -> Coordinate:
        return self.drawing.top_left

    @property
    def size(self) -> Size:
        return self.drawing.size
