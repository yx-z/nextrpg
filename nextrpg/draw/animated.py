from abc import ABC, abstractmethod
from typing import Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import Draw
from nextrpg.draw.group import Group


class Animated(Sizeable, ABC):
    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def draw(self) -> Draw | Group: ...

    @property
    def top_left(self) -> Coordinate:
        return self.draw.top_left

    @property
    def size(self) -> Size:
        return self.draw.size
