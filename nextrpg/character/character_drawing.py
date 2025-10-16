from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.direction import Direction
from nextrpg.geometry.sizable import Sizable


class CharacterDrawing(ABC, Sizable):
    direction: Direction

    @property
    @abstractmethod
    def drawing(self) -> Drawing | DrawingGroup: ...

    @abstractmethod
    def turn(self, direction: Direction) -> Self: ...

    @abstractmethod
    def tick_move(self, time_delta: Millisecond) -> Self: ...

    def tick_idle(self, time_delta: Millisecond) -> Self:
        return self

    def tick_action(self, time_delta: Millisecond, action: Any) -> Self:
        return self

    @cached_property
    def top_left(self) -> Coordinate:
        return self.drawing.top_left

    @cached_property
    def size(self) -> Size:
        return self.drawing.size
