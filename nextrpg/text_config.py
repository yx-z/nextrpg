"""
Text configuration system for NextRPG.

This module provides configuration options for text rendering in NextRPG
games. It includes the `TextConfig` class which defines font, color,
spacing, and rendering options for text display.

The text configuration system features:
- Font selection and sizing
- Color and transparency settings
- Line spacing control for multi-line text
- Antialiasing options for smooth text rendering
- Integration with the global configuration system

Example:
    ```python
    from nextrpg.text_config import TextConfig
    from nextrpg.core import Font, Rgba

    # Create default text config
    config = TextConfig()

    # Create custom text config
    custom_config = TextConfig(
        font=Font(24, "Arial"),
        color=Rgba(255, 255, 0, 255),  # Yellow
        line_spacing=10,
        antialias=True
    )
    ```
"""

from dataclasses import dataclass

from nextrpg.core import WHITE, Font, Pixel, Rgba
from nextrpg.model import export


@export
@dataclass(frozen=True)
class TextConfig:
    """
    Configuration class for text rendering.

    This class defines all parameters needed for text rendering,
    including font selection, color, spacing, and rendering quality.
    It's designed to be immutable for consistent text appearance
    across the application.

    Arguments:
        `font`: The font to use for rendering text. Controls the
            typeface, size, and style of the text.

        `color`: The color to use for rendering text. Includes
            RGB values and alpha transparency.

        `line_spacing`: The vertical spacing between lines in
            multi-line text, measured in pixels.

        `antialias`: Whether to use antialiasing for rendering text.
            Antialiasing creates smoother text edges but may be
            slightly slower to render.

    Example:
        ```python
        from nextrpg.text_config import TextConfig
        from nextrpg.core import Font, Rgba

        # Default configuration
        default_config = TextConfig()

        # Custom configuration for UI text
        ui_config = TextConfig(
            font=Font(16, "Arial"),
            color=Rgba(255, 255, 255, 255),  # White
            line_spacing=5,
            antialias=True
        )

        # Configuration for large titles
        title_config = TextConfig(
            font=Font(48, "Times New Roman"),
            color=Rgba(255, 215, 0, 255),  # Gold
            line_spacing=15,
            antialias=True
        )
        ```
    """

    font: Font = Font(28)
    color: Rgba = WHITE
    line_spacing: Pixel = 8
    antialias: bool = True
