from __future__ import annotations

from dataclasses import dataclass
from math import atan2, degrees, hypot, sqrt
from typing import Iterator, override

from nextrpg.core.dimension import Height, Pixel, Size, Width
from nextrpg.core.direction import Direction, DirectionalOffset
from nextrpg.core.save import LoadFromSaveList


@dataclass(frozen=True)
class Coordinate(LoadFromSaveList[int]):
    input_left: Pixel | Width
    input_top: Pixel | Height

    @property
    def left(self) -> Width:
        if isinstance(self.input_left, Width):
            return self.input_left
        return Width(self.input_left)

    @property
    def top(self) -> Height:
        if isinstance(self.input_top, Height):
            return self.input_top
        return Height(self.input_top)

    @property
    def size(self) -> Size:
        return Size(self.left, self.top)

    @property
    def tuple(self) -> tuple[Pixel, Pixel]:
        return self.left.value, self.top.value

    def __iter__(self) -> Iterator[Width | Height]:
        return iter((self.left, self.top))

    @property
    def negate_left(self) -> Coordinate:
        return Coordinate(-self.left, self.top)

    @property
    def negate_top(self) -> Coordinate:
        return Coordinate(self.left, -self.top)

    def __neg__(self) -> Coordinate:
        return Coordinate(-self.left, -self.top)

    def __add__(
        self, arg: Coordinate | DirectionalOffset | Size | Width | Height
    ) -> Coordinate:
        if isinstance(arg, Width):
            return Coordinate(self.left + arg, self.top)

        if isinstance(arg, Height):
            return Coordinate(self.left, self.top + arg)

        if isinstance(arg, Size):
            return Coordinate(self.left + arg.width, self.top + arg.height)

        if isinstance(arg, Coordinate):
            return Coordinate(self.left + arg.left, self.top + arg.top)

        match arg.direction:
            case Direction.UP:
                return Coordinate(self.left, self.top - arg.offset)
            case Direction.DOWN:
                return Coordinate(self.left, self.top + arg.offset)
            case Direction.LEFT:
                return Coordinate(self.left - arg.offset, self.top)
            case Direction.RIGHT:
                return Coordinate(self.left + arg.offset, self.top)

        diag = arg.offset / sqrt(2)
        match arg.direction:
            case Direction.UP_LEFT:
                return Coordinate(self.left - diag, self.top - diag)
            case Direction.UP_RIGHT:
                return Coordinate(self.left + diag, self.top - diag)
            case Direction.DOWN_LEFT:
                return Coordinate(self.left - diag, self.top + diag)
            case Direction.DOWN_RIGHT:
                return Coordinate(self.left + diag, self.top + diag)

    def __sub__(
        self, arg: DirectionalOffset | Size | Width | Height | Coordinate
    ) -> Coordinate:
        return self + -arg

    def relative_to(self, other: Coordinate) -> Direction:
        dx = self.left - other.left
        dy = self.top - other.top
        angle = (degrees(atan2(-dy.value, dx.value)) + 360) % 360
        closest = min(
            _ANGLE_TO_DIRECTION.items(),
            key=lambda a: _angle_difference(angle, a[0]),
        )
        return closest[1]

    def __repr__(self) -> str:
        return f"({self.left.value:.0f}, {self.top.value:.0f})"

    def distance(self, other: Coordinate) -> Pixel:
        dx = self.left - other.left
        dy = self.top - other.top
        return hypot(dx.value, dy.value)

    @override
    @property
    def save_data(self) -> list[int]:
        return list(self.tuple)


ORIGIN = Coordinate(0, 0)


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
