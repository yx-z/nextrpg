from abc import ABC, abstractmethod
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing


class Animated(ABC):
    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self:
        """"""

    @property
    @abstractmethod
    def drawings(self) -> tuple[Drawing, ...]:
        """"""
