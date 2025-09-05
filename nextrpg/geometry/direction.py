from __future__ import annotations

from dataclasses import dataclass, replace
from enum import auto
from functools import cached_property
from math import cos, radians, sin
from typing import Self

from nextrpg.core.save import LoadFromSaveEnum
from nextrpg.geometry.dimension import Pixel, Size


class Direction(LoadFromSaveEnum):
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    UP_LEFT = auto()
    UP_RIGHT = auto()
    DOWN_LEFT = auto()
    DOWN_RIGHT = auto()

    def __neg__(self) -> Direction:
        return _OPPOSITE_DIRECTION[self]


type Degree = int | float


@dataclass(frozen=True)
class DirectionalOffset:
    direction: Direction | Degree
    offset: Pixel

    def __mul__(self, scale: float) -> Self:
        return replace(self, offset=self.offset * scale)

    def __rmul__(self, scale: float) -> Self:
        return self * scale

    def __truediv__(self, scale: float) -> Self:
        return self * (1.0 / scale)

    @cached_property
    def shift(self) -> Size:
        width = cos(self.radian) * self.offset
        height = sin(self.radian) * self.offset
        return Size(width, height)

    @cached_property
    def radian(self) -> float:
        return radians(self.degree)

    @cached_property
    def degree(self) -> int | float:
        if isinstance(self.direction, int | float):
            return self.direction

        match self.direction:
            case Direction.DOWN:
                return 90
            case Direction.LEFT:
                return 180
            case Direction.RIGHT:
                return 0
            case Direction.UP:
                return 270
            case Direction.UP_LEFT:
                return 225
            case Direction.UP_RIGHT:
                return 315
            case Direction.DOWN_LEFT:
                return 135
            case Direction.DOWN_RIGHT:
                return 45

    def __neg__(self) -> Self:
        offset = -self.offset
        return replace(self, offset=offset)


_OPPOSITE_DIRECTION = {
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
    Direction.UP: Direction.DOWN,
    Direction.UP_LEFT: Direction.DOWN_RIGHT,
    Direction.UP_RIGHT: Direction.DOWN_LEFT,
    Direction.DOWN_LEFT: Direction.UP_RIGHT,
    Direction.DOWN_RIGHT: Direction.UP_LEFT,
}
