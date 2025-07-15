"""
Draw on screen configuration system for NextRPG.

This module provides configuration options for drawing operations
on screen in NextRPG games. It includes the `DrawOnScreenConfig`
class which defines parameters for drawing operations like stroke
width and other rendering properties.

The draw on screen configuration features:
- Configurable stroke width for geometric shapes
- Integration with drawing operations
- Default rendering parameters

Example:
    ```python
    from nextrpg.draw_on_screen_config import DrawOnScreenConfig
    from nextrpg.core import Pixel

    # Create default draw config
    config = DrawOnScreenConfig()

    # Create custom draw config
    custom_config = DrawOnScreenConfig(stroke_width=Pixel(5))
    ```
"""

from dataclasses import dataclass

from nextrpg.core import Pixel
from nextrpg.model import export


@export
@dataclass(frozen=True)
class DrawOnScreenConfig:
    """
    Configuration class for drawing operations on screen.

    This config is used by drawing operations to control
    rendering parameters like stroke width for geometric shapes.

    Arguments:
        `stroke_width`: The width of stroke lines for geometric
            shapes in pixels. Defaults to 2 pixels.

    Example:
        ```python
        from nextrpg.draw_on_screen_config import DrawOnScreenConfig
        from nextrpg.core import Pixel

        # Default configuration (2px stroke)
        config = DrawOnScreenConfig()

        # Thick stroke configuration
        thick_config = DrawOnScreenConfig(stroke_width=Pixel(5))

        # Thin stroke configuration
        thin_config = DrawOnScreenConfig(stroke_width=Pixel(1))
        ```
    """

    stroke_width: Pixel = 2
