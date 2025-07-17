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
from math import ceil
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

    Example:
        ```python
        # Create a size for a sprite
        sprite_size = Size(32, 32)

        # Scale the size
        scaled_size = sprite_size.scale(2.0)  # Returns Size(64, 64)
        ```
    """

    width: Pixel
    height: Pixel

    def scale(self, scaling: float) -> Self:
        """
        Scales the dimensions by a scaling factor and returns a new `Size`.

        The new dimensions are rounded up to the nearest integer to ensure
        that drawings won't leave tiny, black gaps after scaling.

        Arguments:
            `scaling`: A scaling factor by which the width and height will be
                multiplied.

        Returns:
            `Size`: A new `Size` object representing the scaled dimensions.

        Example:
            ```python
            size = Size(10, 20)
            scaled = size.scale(1.5)  # Returns Size(15, 30)
            ```
        """
        return Size(ceil(self.width * scaling), ceil(self.height * scaling))

    def __repr__(self) -> str:
        return f"({self.width}, {self.height})"
