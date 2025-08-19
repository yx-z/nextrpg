from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.direction import Direction
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing


@dataclass(frozen=True)
class CharacterDrawing(ABC):
    direction: Direction

    def bottom_center_to_top_left(
        self, bottom_center: Coordinate
    ) -> Coordinate:
        return bottom_center - self.drawing.width / 2 - self.drawing.height

    @property
    @abstractmethod
    def drawing(self) -> Drawing: ...

    @abstractmethod
    def turn(self, direction: Direction) -> Self: ...

    @abstractmethod
    def tick_move(self, time_delta: Millisecond) -> Self: ...

    @abstractmethod
    def tick_idle(self, time_delta: Millisecond) -> Self: ...
