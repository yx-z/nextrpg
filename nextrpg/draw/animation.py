from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizable import Sizable
from nextrpg.core.time import Millisecond

if TYPE_CHECKING:
    from nextrpg.draw.drawing import Drawing
    from nextrpg.draw.drawing_group import DrawingGroup


class Animation(Sizable, ABC):
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
