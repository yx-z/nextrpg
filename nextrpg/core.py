"""
Core types referenced across `nextrpg`.
"""

from __future__ import annotations

from enum import Enum, auto
from math import ceil

from nextrpg.model import Model


class Rgba(Model):
    """
    Represents an RGBA color with red, green, blue and alpha components.

    Arguments:
        `red`: The red component of the color (0-255).

        `green`: The green component of the color (0-255).

        `blue`: The blue component of the color (0-255).

        `alpha`: The alpha (opacity) component of the color (0-255).
    """

    red: int
    green: int
    blue: int
    alpha: int

    @property
    def tuple(self) -> tuple[int, int, int, int]:
        """
        Gets the color components as a tuple.

        Returns:
            `tuple[int, int, int, int]`: A tuple containing the red, green,
            blue and alpha values in that order.
        """
        return self.red, self.green, self.blue, self.alpha


type Millisecond = int
"""
Millisecond elapsed between game loops.
"""


class Direction(Enum):
    """
    Represents eight directional movements.

    Attributes:

        `DOWN`: Move down and toward the bottom of the screen.

        `LEFT`: Move left and toward the left of the screen.

        `RIGHT`: Move right and toward the right of the screen.

        `UP`: Move up and toward the top of the screen.

        `UP_LEFT`: Move up and left diagonally.

        `UP_RIGHT`: Move up and right diagonally.

        `DOWN_LEFT`: Move down and left diagonally.

        `DOWN_RIGHT`: Move down and right diagonally.
    """

    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    UP_LEFT = auto()
    UP_RIGHT = auto()
    DOWN_LEFT = auto()
    DOWN_RIGHT = auto()


type Pixel = int | float
"""
Number of pixel on screen.

`float` is allowed given Pygame supports passing `float` as `Rect`.
"""


class DirectionalOffset(Model):
    """
    Represents a directional offset for movement calculations.

    This class combines a direction (one of eight possible directions) with
    an offset value to define movement in 2D space. The vector can be used
    with coordinates to calculate new positions.

    Attributes:
        `direction`: The direction of the vector, defined by `Direction` enum.
            Supports both orthogonal (`UP`, `DOWN`, `LEFT`, `RIGHT`)
            and diagonal (`UP_LEFT`, `UP_RIGHT`, `DOWN_LEFT`, `DOWN_RIGHT`).

        `offset`: The length of movement in pixels.
            This value will be decomposed into x, y pixels upon diagnoal moves.
    """

    direction: Direction
    offset: Pixel


class Size(Model):
    """
    Represents the dimensions of a two-dimensional space, such as an image,
    with defined width and height.

    This class is immutable and designed to encapsulate the concept of size
    in pixel measurements.

    Attributes:
        `width`: The width of the size in pixels.

        `height`: The height of the size in pixels.
    """

    width: Pixel
    height: Pixel

    def __post_init__(self) -> None:
        if self.width < 0 or self.height < 0:
            raise ValueError(
                f"{self.width=} and {self.height=} cannot be negative."
            )

    def __mul__(self, scale: float) -> Size:
        """
        Scales the dimensions by a scaling factor and returns a new `Size`.

        The new dimensions are rounded up to the nearest integer.

        Round up so that drawings won't leave tiny, black gaps after scaled.

        Args:
            `scale`: A scaling factor by which the width and height will be
                multiplied.

        Returns:
            `Size`: A new `Size` object representing the scaled dimensions.
        """
        return Size(ceil(self.width * scale), ceil(self.height * scale))

    @property
    def tuple(self) -> tuple[Pixel, Pixel]:
        """
        Gets the dimensions as a tuple.

        Returns:
            `tuple[Pixel, Pixel]`: A tuple containing the width and height
                values in that order.
        """
        return self.width, self.height
