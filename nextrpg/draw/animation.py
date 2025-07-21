from abc import ABC, abstractmethod
from typing import Self

from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.core.time import Millisecond


class Animation(ABC):
    @property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        """ """

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self:
        """ """
