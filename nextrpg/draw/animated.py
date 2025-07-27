from abc import ABC, abstractmethod
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg import Draw
from nextrpg.draw.drawing_group import DrawingGroup


class Animated(ABC):
    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self:
        """"""

    @property
    @abstractmethod
    def drawings(self) -> tuple[Draw | DrawingGroup, ...]:
        """"""
