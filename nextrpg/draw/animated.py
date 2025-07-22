from abc import ABC, abstractmethod
from typing import Self

from nextrpg.draw.draw_on_screen import Drawing
from nextrpg.core.time import Millisecond


class Animated(ABC):
    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self:
        """"""

    @property
    @abstractmethod
    def drawings(self) -> tuple[Drawing, ...]:
        """"""
