from __future__ import annotations

from abc import ABC, abstractmethod
from collections import namedtuple
from math import atan2, degrees, hypot, sqrt
from typing import Self

from nextrpg.core.dimension import Pixel, Size
from nextrpg.core.direction import Direction, DirectionalOffset
from nextrpg.core.time import Millisecond


class Coordinate(namedtuple("Coordinate", "left top")):
    left: Pixel
    top: Pixel

    @property
    def negate_left(self) -> Coordinate:
        return Coordinate(-self.left, self.top)

    @property
    def negate_top(self) -> Coordinate:
        return Coordinate(self.left, -self.top)

    def __neg__(self) -> Coordinate:
        return Coordinate(-self.left, -self.top)

    def __add__(
        self, offset: DirectionalOffset | Size | Coordinate
    ) -> Coordinate:
        if isinstance(offset, (Coordinate, Size)):
            x, y = offset
            return Coordinate(self.left + x, self.top + y)

        match offset.direction:
            case Direction.UP:
                return Coordinate(self.left, self.top - offset.offset)
            case Direction.DOWN:
                return Coordinate(self.left, self.top + offset.offset)
            case Direction.LEFT:
                return Coordinate(self.left - offset.offset, self.top)
            case Direction.RIGHT:
                return Coordinate(self.left + offset.offset, self.top)

        diag = offset.offset / sqrt(2)
        match offset.direction:
            case Direction.UP_LEFT:
                return Coordinate(self.left - diag, self.top - diag)
            case Direction.UP_RIGHT:
                return Coordinate(self.left + diag, self.top - diag)
            case Direction.DOWN_LEFT:
                return Coordinate(self.left - diag, self.top + diag)
            case Direction.DOWN_RIGHT:
                return Coordinate(self.left + diag, self.top + diag)

    def __sub__(
        self, offset: DirectionalOffset | Size | Coordinate
    ) -> Coordinate:
        return self + -offset

    def relative_to(self, other: Coordinate) -> Direction:
        dx = self.left - other.left
        dy = self.top - other.top
        angle = (degrees(atan2(-dy, dx)) + 360) % 360
        closest = min(
            _ANGLE_TO_DIRECTION.items(),
            key=lambda a: _angle_difference(angle, a[0]),
        )
        return closest[1]

    def __str__(self) -> str:
        return f"({self.left:.0f}, {self.top:.0f})"

    def distance(self, other: Coordinate) -> Pixel:
        dx = self.left - other.left
        dy = self.top - other.top
        return hypot(dx, dy)


ORIGIN = Coordinate(0, 0)


class Moving(ABC):
    coordinate: Coordinate

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...


def _angle_difference(a1: float, a2: float) -> float:
    return abs((a1 - a2 + 180) % 360 - 180)


_ANGLE_TO_DIRECTION = {
    0: Direction.RIGHT,
    45: Direction.UP_RIGHT,
    90: Direction.UP,
    135: Direction.UP_LEFT,
    180: Direction.LEFT,
    225: Direction.DOWN_LEFT,
    270: Direction.DOWN,
    315: Direction.DOWN_RIGHT,
}
