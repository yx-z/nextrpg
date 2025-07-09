from collections import namedtuple
from functools import cached_property
from math import atan2, degrees, sqrt
from typing import Self

from nextrpg.core import Direction, DirectionalOffset, Pixel


class Coordinate(namedtuple("Coordinate", "left top")):
    """
    Represents a 2D coordinate with immutability and provides methods
    for scaling and shifting coordinates.

    Attributes:
        `left`: The horizontal position of the coordinate, measured by
            the number of pixels from the left edge of the game window.

        `top`: The vertical position of the coordinate, measured by
            the number of pixels from the top edge of the game window.
    """

    left: Pixel
    top: Pixel

    @cached_property
    def negate(self) -> Self:
        return Coordinate(-self.left, -self.top)

    def shift(self, offset: DirectionalOffset | Self) -> Self:
        """
        Shifts the coordinate in the specified direction by a given offset.
        Supports both orthogonal and diagonal directions.

        Or add two coordinates together.

        For diagonal directions, the offset is divided proportionally.
        For example, an offset of `sqrt(2)` in `UP_LEFT` direction shifts
        the coordinate `Pixel(1)` in both `UP` and `LEFT` directions.

        Arguments:
            `offset`: A `DirectionalOffset` representing the direction
                and offset, or `Coordinate` to add to the current `Coordinate`.

        Returns:
            `Coordinate`: A new coordinate shifted by the specified offset in
            the given direction.
        """
        if isinstance(offset, Coordinate):
            return Coordinate(self.left + offset.left, self.top + offset.top)

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

    def relative_to(self, other: Coordinate) -> Direction:
        dx = self.left - other.left
        dy = self.top - other.top
        angle = (degrees(atan2(-dy, dx)) + 360) % 360
        closest = min(
            _ANGLE_TO_DIRECTION.items(),
            key=lambda a: _angle_difference(angle, a[0]),
        )
        return closest[1]

    def __repr__(self) -> str:
        return f"({self.left:.1f}, {self.top:.1f})"

    def distance(self, other: Coordinate) -> Pixel:
        dx = self.left - other.left
        dy = self.top - other.top
        return sqrt(dx**2 + dy**2)


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
