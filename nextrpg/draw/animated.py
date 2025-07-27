from abc import ABC, abstractmethod
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg import Draw
from nextrpg.draw.group import Group


class Animated(ABC):
    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self:
        """"""

    @property
    @abstractmethod
    def draw(self) -> Draw | Group:
        """"""
