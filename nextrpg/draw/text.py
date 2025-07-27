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
from pygame import Surface

from nextrpg import Coordinate, Draw
from nextrpg.draw.drawing_group import DrawingGroup, DrawRelativeTo
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
        text_sizes = tuple(
            self.config.font.text_size(line) for line in self._lines
        )
        width = max(s.width for s in text_sizes)
        height = sum(s.height for s in text_sizes)
        spacings = self.config.line_spacing * (len(self._lines) - 1)
        return Size(width, height + spacings)

    @cached_property
    def drawing_group(self) -> DrawingGroup:
        leader = self._drawing(self._lines[0])
        followers = tuple(
            DrawRelativeTo(self._drawing(line), self._line_shift(i))
            for i, line in enumerate(self._lines[1:], start=1)
        )
        return DrawingGroup(leader, followers)

    @cached_property
    def _lines(self) -> tuple[str, ...]:
        return tuple(self.message.splitlines())

    def _line_shift(self, index: int) -> Coordinate:
        height = self.config.font.text_height + self.config.line_spacing
        shift = height * index
        return Coordinate(0, shift)

    def _drawing(self, line: str) -> Draw:
        surface = self.config.font.pygame.render(
            line, self.config.antialias, self.config.color
        )
        return Draw(surface)
