"""
Draw on screen configuration system for `nextrpg`.

This module provides configuration options for drawing operations on screen in
`nextrpg` games. It includes the `DrawOnScreenConfig` class which defines
parameters for drawing operations like stroke width and other rendering
properties.

Features:
    - Configurable stroke width for geometric shapes
    - Integration with drawing operations
    - Default rendering parameters
"""

from dataclasses import dataclass

from nextrpg.core import Pixel
from nextrpg.model import export


@export
@dataclass(frozen=True)
class DrawOnScreenConfig:
    """
    Configuration class for drawing operations on screen.

    This config is used by drawing operations to control rendering parameters
    like stroke width for geometric shapes.

    Arguments:
        stroke_width: The width of stroke lines for geometric shapes in pixels.
            Defaults to 2 pixels.
    """

    stroke_width: Pixel = 2
