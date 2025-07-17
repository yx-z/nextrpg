"""
Text rendering and layout utilities for `NextRPG`.

This module provides text rendering capabilities for `NextRPG` games. It
includes the `Text` class which handles text layout, sizing, and line
management for multi-line text rendering.

The text system features:
- Multi-line text support with automatic line wrapping
- Configurable font and styling options
- Automatic text sizing and layout calculations
- Line height and spacing management
- Integration with the global configuration system
"""

from dataclasses import dataclass, field
from functools import cached_property

from nextrpg.core.dimension import Pixel, Size
from nextrpg.global_config.global_config import config

from nextrpg.global_config.text_config import TextConfig


@dataclass(frozen=True)
class Text:
    """
    Represents a text message with layout and sizing capabilities.

    This class provides text rendering functionality with support for multi-line
    text, automatic sizing, and configurable styling. It handles text layout
    calculations and provides properties for accessing text dimensions and line
    information.

    Arguments:
        `message`: The text message to be rendered. Can contain newline
            characters for multi-line text.
        `global_config`: The text configuration including font and styling options.
            Defaults to the global text configuration.
    """

    message: str
    config: TextConfig = field(default_factory=lambda: config().text)

    @cached_property
    def size(self) -> Size:
        """
        Get the total size required to render the text.

        Calculates the dimensions needed to display the text,
        including line spacing between multi-line text.
        Returns a zero size for empty messages.

        Returns:
            `Size`: The width and height required to render the text.

        Example:
            ```python
            text = Text("Hello\nWorld!")
            size = text.size  # Returns Size(width, height)
            ```
        """
        if not self.message:
            return Size(0, 0)
        text_sizes = tuple(
            self.config.font.text_size(line) for line in self.lines
        )
        width = max(s.width for s in text_sizes)
        height = sum(s.height for s in text_sizes)
        spacings = self.config.line_spacing * (len(self.lines) - 1)
        return Size(width, height + spacings)

    @cached_property
    def line_heights(self) -> tuple[Pixel, ...]:
        """
        Get the vertical position of each line in the text.

        Returns a list of pixel positions where each line should
        be rendered, taking into account line spacing.

        Returns:
            `list[Pixel]`: List of vertical positions for each line.

        Example:
            ```python
            text = Text("Line 1\nLine 2\nLine 3")
            heights = text.line_heights  # [0, 20, 40] (example)
            ```
        """
        return tuple(
            (self.config.font.text_height + self.config.line_spacing) * i
            for i in range(len(self.lines))
        )

    @cached_property
    def lines(self) -> tuple[str, ...]:
        """
        Get the individual lines of the text message.

        Splits the message on newline characters to create a list
        of individual lines for rendering.

        Returns:
            `list[str]`: List of text lines.

        Example:
            ```python
            text = Text("First line\nSecond line\nThird line")
            lines = text.lines  # ["First line", "Second line", "Third line"]
            ```
        """
        return tuple(self.message.splitlines())
