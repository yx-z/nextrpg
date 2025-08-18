from __future__ import annotations

from math import atan2, degrees, hypot, sqrt
from typing import NamedTuple, Self

from nextrpg.core.dimension import Height, Pixel, Size, Width
from nextrpg.core.direction import Direction, DirectionalOffset


class Coordinate(NamedTuple):
    left_value: Pixel
    top_value: Pixel

    @property
    def left(self) -> Width:
        return Width(self.left_value)

    @property
    def top(self) -> Height:
        return Height(self.top_value)

    @property
    def size(self) -> Size:
        return Size(self.left_value, self.top_value)

    @property
    def negate_left(self) -> Coordinate:
        return Coordinate(-self.left_value, self.top_value)

    @property
    def negate_top(self) -> Coordinate:
        return Coordinate(self.left_value, -self.top_value)

    def __neg__(self) -> Coordinate:
        return Coordinate(-self.left_value, -self.top_value)

    def __add__(
        self, arg: Coordinate | DirectionalOffset | Size | Width | Height
    ) -> Coordinate:
        if isinstance(arg, Width):
            return Coordinate(self.left_value + arg.value, self.top_value)

        if isinstance(arg, Height):
            return Coordinate(self.left_value, self.top_value + arg.value)

        if isinstance(arg, Size):
            return Coordinate(
                self.left_value + arg.width_value,
                self.top_value + arg.height_value,
            )

        if isinstance(arg, Coordinate):
            return Coordinate(
                self.left_value + arg.left_value, self.top_value + arg.top_value
            )

        match arg.direction:
            case Direction.UP:
                return Coordinate(self.left_value, self.top_value - arg.offset)
            case Direction.DOWN:
                return Coordinate(self.left_value, self.top_value + arg.offset)
            case Direction.LEFT:
                return Coordinate(self.left_value - arg.offset, self.top_value)
            case Direction.RIGHT:
                return Coordinate(self.left_value + arg.offset, self.top_value)

        diag = arg.offset / sqrt(2)
        match arg.direction:
            case Direction.UP_LEFT:
                return Coordinate(self.left_value - diag, self.top_value - diag)
            case Direction.UP_RIGHT:
                return Coordinate(self.left_value + diag, self.top_value - diag)
            case Direction.DOWN_LEFT:
                return Coordinate(self.left_value - diag, self.top_value + diag)
            case Direction.DOWN_RIGHT:
                return Coordinate(self.left_value + diag, self.top_value + diag)

    def __sub__(
        self, arg: DirectionalOffset | Size | Width | Height | Coordinate
    ) -> Coordinate:
        return self + -arg

    def relative_to(self, other: Coordinate) -> Direction:
        dx = self.left_value - other.left_value
        dy = self.top_value - other.top_value
        angle = (degrees(atan2(-dy, dx)) + 360) % 360
        closest = min(
            _ANGLE_TO_DIRECTION.items(),
            key=lambda a: _angle_difference(angle, a[0]),
        )
        return closest[1]

    def __repr__(self) -> str:
        return f"({self.left_value:.0f}, {self.top_value:.0f})"

    def distance(self, other: Coordinate) -> Pixel:
        dx = self.left_value - other.left_value
        dy = self.top_value - other.top_value
        return hypot(dx, dy)

    @property
    def save_data(self) -> list[Pixel]:
        return list(self)

    @classmethod
    def load(cls, data: list[Pixel]) -> Self:
        return cls(*data)


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
