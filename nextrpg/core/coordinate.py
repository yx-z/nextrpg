"""
2D coordinate system for `nextrpg`.

This module provides a comprehensive 2D coordinate system for positioning and
movement in `nextrpg` games. It includes the `Coordinate` class which
represents positions in 2D space with support for directional movement,
scaling, and mathematical operations.

Features:
    - Immutable coordinate representation
    - Directional movement with `DirectionalOffset`
    - Distance calculations between coordinates
    - Direction calculation between two points
    - Coordinate arithmetic (addition, negation)
    - Support for both orthogonal and diagonal movement
"""

from abc import ABC, abstractmethod
from collections import namedtuple
from math import atan2, degrees, hypot, sqrt
from typing import Self

from nextrpg.core.dimension import Pixel, Size
from nextrpg.core.direction import Direction, DirectionalOffset
from nextrpg.core.time import Millisecond


class Coordinate(namedtuple("Coordinate", "left top")):
    """
    Represents a 2D coordinate with immutability and mathematical operations.

    This class provides a comprehensive 2D coordinate system with support for
    directional movement, distance calculations, and coordinate arithmetic. It's
    designed to be immutable for thread safety and predictable behavior.

    The coordinate system uses a top-left origin where (0, 0) is the top-left
    corner of the screen, with positive x extending right and positive y
    extending down.

    Arguments:
        left: The horizontal position of the coordinate, measured by the number
            of pixels from the left edge of the game window.
        top: The vertical position of the coordinate, measured by the number of
            pixels from the top edge of the game window.
    """

    left: Pixel
    top: Pixel

    @property
    def negate_left(self) -> Self:
        return Coordinate(-self.left, self.top)

    @property
    def negate_top(self) -> Self:
        return Coordinate(self.left, -self.top)

    def __neg__(self) -> Self:
        return Coordinate(-self.left, -self.top)

    def __add__(self, offset: DirectionalOffset | Size | Self) -> Self:
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

    def __sub__(self, offset: DirectionalOffset | Size | Self) -> Self:
        return self + -offset

    def relative_to(self, other: Self) -> Direction:
        """
        Calculate the direction from another coordinate to this one.

        Determines the primary direction from the other coordinate to this
        coordinate by calculating the angle and mapping it to the nearest of the
        eight possible directions.

        Arguments:
            other: The reference coordinate to calculate direction from.

        Returns:
            The direction from the other coordinate to this one.
        """
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

    def distance(self, other: Self) -> Pixel:
        """
        Calculate the Euclidean distance to another coordinate.

        Arguments:
            other: The coordinate to calculate distance to.

        Returns:
            The distance between the two coordinates.
        """
        dx = self.left - other.left
        dy = self.top - other.top
        return hypot(dx, dy)


class Moving(ABC):
    coordinate: Coordinate

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self:
        """"""


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
