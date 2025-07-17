"""
Text configuration system for `NextRPG`.

This module provides configuration options for text rendering in `NextRPG`
games. It includes the `TextConfig` class which defines font, color, spacing,
and rendering options for text display.

The text configuration system features:
- Font selection and sizing
- Color and transparency settings
- Line spacing control for multi-line text
- Antialiasing options for smooth text rendering
- Integration with the global configuration system
"""

from dataclasses import dataclass

from nextrpg.core.color import WHITE, Rgba
from nextrpg.core.dimension import Pixel
from nextrpg.core.font import Font


@dataclass(frozen=True)
class TextConfig:
    """
    Configuration class for text rendering.

    This class defines all parameters needed for text rendering, including font
    selection, color, spacing, and rendering quality. It's designed to be
    immutable for consistent text appearance across the application.

    Arguments:
        `font`: The font to use for rendering text. Controls the typeface, size,
            and style of the text.
        `color`: The color to use for rendering text. Includes RGB values and
            alpha transparency.
        `line_spacing`: The vertical spacing between lines in multi-line text,
            measured in pixels.
        `antialias`: Whether to use antialiasing for rendering text.
            Antialiasing creates smoother text edges but may be slightly slower
            to render.
    """

    font: Font = Font(28)
    color: Rgba = WHITE
    line_spacing: Pixel = 8
    antialias: bool = True
