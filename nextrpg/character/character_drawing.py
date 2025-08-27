from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.direction import Direction
from nextrpg.core.sizable import Sizable
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing


@dataclass(frozen=True)
class CharacterDrawing(ABC, Sizable):
    direction: Direction

    @property
    @abstractmethod
    def drawing(self) -> Drawing: ...

    @abstractmethod
    def turn(self, direction: Direction) -> Self: ...

    @abstractmethod
    def tick_move(self, time_delta: Millisecond) -> Self: ...

    @abstractmethod
    def tick_idle(self, time_delta: Millisecond) -> Self: ...

    @property
    def top_left(self) -> Coordinate:
        return self.drawing.top_left

    @property
    def size(self) -> Size:
        return self.drawing.size
