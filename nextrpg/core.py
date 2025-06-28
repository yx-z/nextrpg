"""
Core types referenced across `nextrpg`.
"""

from __future__ import annotations

from collections import namedtuple
from enum import Enum, auto
from math import ceil
from typing import NamedTuple

type Alpha = int
"""
Alpha channel that defines the transparency between [0, 255] for images.
0 is fully transparent, 255 is fully opaque.
"""


class Rgba(namedtuple("Rgba", "red green blue alpha")):
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
    alpha: Alpha


type Millisecond = int | float
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


class DirectionalOffset(NamedTuple):
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


class Size(namedtuple("Size", "width height")):
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

    def scale(self, scaling: float) -> Size:
        """
        Scales the dimensions by a scaling factor and returns a new `Size`.

        The new dimensions are rounded up to the nearest integer.

        Round up so that drawings won't leave tiny, black gaps after scaled.

        Args:
            `scaling`: A scaling factor by which the width and height will be
                multiplied.

        Returns:
            `Size`: A new `Size` object representing the scaled dimensions.
        """
        return Size(ceil(self.width * scaling), ceil(self.height * scaling))
