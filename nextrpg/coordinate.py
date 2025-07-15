"""
2D coordinate system for NextRPG.

This module provides a comprehensive 2D coordinate system for positioning
and movement in NextRPG games. It includes the `Coordinate` class which
represents positions in 2D space with support for directional movement,
scaling, and mathematical operations.

The coordinate system features:
- Immutable coordinate representation
- Directional movement with `DirectionalOffset`
- Distance calculations between coordinates
- Direction calculation between two points
- Coordinate arithmetic (addition, negation)
- Support for both orthogonal and diagonal movement

The system is designed to work seamlessly with the drawing and
movement systems, providing precise positioning for all game elements.

Example:
    ```python
    from nextrpg.draw.coordinate import Coordinate
    from nextrpg.core import Direction, DirectionalOffset

    # Create coordinates
    pos1 = Coordinate(100, 200)
    pos2 = Coordinate(150, 250)

    # Calculate distance
    distance = pos1.distance(pos2)

    # Move in a direction
    offset = DirectionalOffset(Direction.UP, 50)
    new_pos = pos1.shift(offset)

    # Get direction between points
    direction = pos2.relative_to(pos1)
    ```
"""

from collections import namedtuple
from functools import cached_property
from math import atan2, degrees, hypot, sqrt
from typing import Self

from nextrpg.core import Direction, DirectionalOffset, Pixel
from nextrpg.model import export


@export
class Coordinate(namedtuple("Coordinate", "left top")):
    """
    Represents a 2D coordinate with immutability and mathematical operations.

    This class provides a comprehensive 2D coordinate system with support
    for directional movement, distance calculations, and coordinate
    arithmetic. It's designed to be immutable for thread safety and
    predictable behavior.

    The coordinate system uses a top-left origin where (0, 0) is the
    top-left corner of the screen, with positive x extending right and
    positive y extending down.

    Arguments:
        `left`: The horizontal position of the coordinate, measured by
            the number of pixels from the left edge of the game window.

        `top`: The vertical position of the coordinate, measured by
            the number of pixels from the top edge of the game window.

    Example:
        ```python
        from nextrpg.draw.coordinate import Coordinate
        from nextrpg.core import Direction, DirectionalOffset

        # Create a coordinate
        pos = Coordinate(100, 200)

        # Move in a direction
        offset = DirectionalOffset(Direction.RIGHT, 50)
        new_pos = pos.shift(offset)  # (150, 200)

        # Calculate distance
        other_pos = Coordinate(150, 250)
        distance = pos.distance(other_pos)
        ```
    """

    left: Pixel
    top: Pixel

    @cached_property
    def negate(self) -> Self:
        """
        Get the negated coordinate.

        Returns a new coordinate with both x and y components negated.
        This is useful for reversing directions or creating opposite
        positions.

        Returns:
            `Coordinate`: A new coordinate with negated components.

        Example:
            ```python
            pos = Coordinate(100, 200)
            negated = pos.negate  # (-100, -200)
            ```
        """
        return Coordinate(-self.left, -self.top)

    def shift(self, offset: DirectionalOffset | Self) -> Self:
        """
        Shift the coordinate by a directional offset or add another coordinate.

        This method supports two modes of operation:
        1. Shifting by a `DirectionalOffset` for directional movement
        2. Adding another `Coordinate` for coordinate arithmetic

        For diagonal directions, the offset is divided proportionally
        using the square root of 2 to maintain consistent movement speed.

        Arguments:
            `offset`: A `DirectionalOffset` representing the direction
                and offset, or `Coordinate` to add to the current coordinate.

        Returns:
            `Coordinate`: A new coordinate shifted by the specified offset
                in the given direction.

        Example:
            ```python
            from nextrpg.core import Direction, DirectionalOffset

            pos = Coordinate(100, 200)

            # Shift by direction
            offset = DirectionalOffset(Direction.UP, 50)
            new_pos = pos.shift(offset)  # (100, 150)

            # Add coordinates
            other = Coordinate(25, 30)
            result = pos.shift(other)  # (125, 230)
            ```
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
        """
        Calculate the direction from another coordinate to this one.

        Determines the primary direction from the other coordinate to
        this coordinate by calculating the angle and mapping it to the
        nearest of the eight possible directions.

        Arguments:
            `other`: The reference coordinate to calculate direction from.

        Returns:
            `Direction`: The direction from the other coordinate to this one.

        Example:
            ```python
            from nextrpg.core import Direction

            pos1 = Coordinate(100, 100)
            pos2 = Coordinate(150, 50)

            direction = pos2.relative_to(pos1)  # Direction.UP_RIGHT
            ```
        """
        dx = self.left - other.left
        dy = self.top - other.top
        angle = (degrees(atan2(-dy, dx)) + 360) % 360
        closest = min(
            _ANGLE_TO_DIRECTION.items(),
            key=lambda a: _angle_difference(angle, a[0]),
        )
        return closest[1]

    def __repr__(self) -> str:
        """
        Get a string representation of the coordinate.

        Returns:
            `str`: A formatted string showing the coordinate values.
        """
        return f"({self.left:.1f}, {self.top:.1f})"

    def distance(self, other: Coordinate) -> Pixel:
        """
        Calculate the Euclidean distance to another coordinate.

        Arguments:
            `other`: The coordinate to calculate distance to.

        Returns:
            `Pixel`: The distance between the two coordinates.

        Example:
            ```python
            pos1 = Coordinate(0, 0)
            pos2 = Coordinate(3, 4)
            distance = pos1.distance(pos2)  # 5.0
            ```
        """
        dx = self.left - other.left
        dy = self.top - other.top
        return hypot(dx, dy)


def _angle_difference(a1: float, a2: float) -> float:
    """
    Calculate the smallest angle difference between two angles.

    This function calculates the shortest angular distance between
    two angles, handling the wraparound at 360 degrees.

    Arguments:
        `a1`: First angle in degrees.

        `a2`: Second angle in degrees.

    Returns:
        `float`: The smallest angle difference in degrees.
    """
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
