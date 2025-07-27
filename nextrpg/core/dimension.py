"""
Core types and utilities used throughout the `nextrpg` framework.

This module provides fundamental data structures and utilities that are
referenced across the entire `nextrpg` framework. It includes:

- Color representation (`Rgba`)
- Directional movement (`Direction`, `DirectionalOffset`)
- Size and dimension handling (`Size`)
- Font management (`Font`)
- Timer utilities (`Timer`)
- Type aliases for common concepts

These types form the foundation for character movement, drawing, and game
mechanics throughout the framework.
"""

from collections import namedtuple
from math import sqrt
from typing import Self

type Pixel = int | float
"""
Number of pixel on screen.

`float` is allowed given Pygame supports passing `float` as `Rect`.
"""

type PixelPerMillisecond = int | float
"""
Used as a unit for speed.
"""


class Size(namedtuple("Size", "width height")):
    """
    Represents the dimensions of a two-dimensional space.

    This class is immutable and designed to encapsulate the concept of size
    in pixel measurements. It provides utility methods for scaling and
    manipulation of dimensions.

    Arguments:
        `width`: The width of the size in pixels.

        `height`: The height of the size in pixels.
    """

    width: Pixel
    height: Pixel

    def __neg__(self) -> Self:
        return Size(-self.width, -self.height)

    def __add__(self, other: Self) -> Self:
        return Size(self.width + other.width, self.height + other.height)

    def __sub__(self, other: Self) -> Self:
        return self + -other

    def __mul__(self, scaling: float) -> Self:
        dimension_scaling = sqrt(scaling)
        width = self.width * dimension_scaling
        height = self.height * dimension_scaling
        return Size(width, height)

    def __truediv__(self, scaling: float) -> Self:
        return self * (1 / scaling)

    def all_dimension_scale(self, scaling: float) -> Self:
        return Size(self.width * scaling, self.height * scaling)

    def __str__(self) -> str:
        return f"({self.width:.0f}, {self.height:.0f})"
