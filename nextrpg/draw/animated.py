from abc import ABC, abstractmethod
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen


class Animated(ABC):
    @property
    @abstractmethod
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        """ """

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self:
        """ """
