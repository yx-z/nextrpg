from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from nextrpg.core.direction import Direction
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import Draw


@dataclass(frozen=True)
class CharacterDraw(ABC):
    direction: Direction

    @property
    @abstractmethod
    def draw(self) -> Draw: ...

    @abstractmethod
    def turn(self, direction: Direction) -> Self: ...

    @abstractmethod
    def tick_move(self, time_delta: Millisecond) -> Self: ...

    @abstractmethod
    def tick_idle(self, time_delta: Millisecond) -> Self: ...
