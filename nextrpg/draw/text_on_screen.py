"""
Text rendering on screen for `NextRPG`.

This module provides text rendering functionality for displaying text on screen
in `NextRPG` games. It includes the `TextOnScreen` class which handles text
positioning and rendering.

The text on screen system features:
- Text positioning and layout
- Multi-line text support
- Font rendering and styling
- Integration with drawing system
"""

from dataclasses import dataclass
from functools import cached_property

from pygame import Surface

from nextrpg import Draw
from nextrpg.core.coordinate import Coordinate
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.text import Text


@dataclass(frozen=True)
class TextOnScreen:
    """
    Text printed on screen.

    This class represents text that is positioned and rendered on the game
    screen. It handles text layout, positioning, and conversion to drawable
    elements.

    Arguments:
        `top_left`: The top-left coordinate of the text.
        `text`: The text object to render.
    """

    top_left: Coordinate
    text: Text

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the text rendered on screen as drawable elements.

        Converts the text into a series of drawable elements,
        one for each line of text, positioned correctly on screen.

        Returns:
            `tuple[DrawOnScreen, ...]`: The text rendered on screen.
        """
        return self.text.group.draw_on_screens(self.top_left)
