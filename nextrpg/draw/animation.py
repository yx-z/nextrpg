from abc import ABC, abstractmethod
from typing import Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizable import Sizable
from nextrpg.core.time import Millisecond


class Animation(Sizable, ABC):
    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def drawing(self) -> "Drawing | Group": ...

    @property
    def top_left(self) -> Coordinate:
        return self.drawing.top_left

    @property
    def size(self) -> Size:
        return self.drawing.size
