from dataclasses import dataclass
from functools import cached_property

import pygame
from pygame.font import SysFont

from nextrpg.core.dimension import Pixel, Size


@dataclass(frozen=True)
class Font:
    """
    Font configuration for text rendering in the game.

    This class provides a convenient way to configure fonts for text
    rendering. It supports both system fonts and custom font files,
    with automatic pygame font object creation.

    Arguments:
        `size`: Font size in pixels.

        `name`: Font name. If `None`, uses the default system font.

    Example:
        ```python
        # Create a font with default system font
        font = Font(16)

        # Create a font with specific name
        custom_font = Font(24, "Arial")

        # Get text dimensions
        text_size = font.text_size("Hello World")
        ```
    """

    size: int
    name: str | None = None

    @cached_property
    def pygame(self) -> pygame.Font:
        """
        Get the pygame font object.

        Creates and caches a pygame Font object based on the font
        configuration. This is used internally for text rendering.

        Returns:
            `pygame.Font`: Pygame font object for text rendering.
        """
        return SysFont(self.name, self.size)

    def text_size(self, text: str) -> Size:
        """
        Get the drawing size of a text string.

        Calculates the pixel dimensions required to render the given
        text string with this font configuration.

        Arguments:
            `text`: The text string to measure.

        Returns:
            `Size`: The size of the text string in pixels.

        Example:
            ```python
            font = Font(16)
            size = font.text_size("Hello")  # Returns Size(width, height)
            ```
        """
        width, height = self.pygame.size(text)
        return Size(width, height)

    @property
    def text_height(self) -> Pixel:
        """
        Get the line height of the font.

        Returns:
            `Pixel`: The line height in pixels.
        """
        return self.pygame.get_linesize()
