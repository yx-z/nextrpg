"""
Text rendering on screen for NextRPG.

This module provides text rendering functionality for displaying
text on screen in NextRPG games. It includes the `TextOnScreen`
class which handles text positioning and rendering.

The text on screen system features:
- Text positioning and layout
- Multi-line text support
- Font rendering and styling
- Integration with drawing system

Example:
    ```python
    from nextrpg.text_on_screen import TextOnScreen
    from nextrpg.text import Text
    from nextrpg.coordinate import Coordinate

    # Create text
    text = Text("Hello, World!")
    position = Coordinate(100, 200)

    # Create text on screen
    text_on_screen = TextOnScreen(top_left=position, text=text)

    # Get drawings for rendering
    drawings = text_on_screen.draw_on_screens
    ```
"""

from dataclasses import dataclass
from functools import cached_property

from pygame import Surface

from nextrpg.coordinate import Coordinate
from nextrpg.draw_on_screen import Drawing, DrawOnScreen
from nextrpg.model import export
from nextrpg.text import Text


@export
@dataclass(frozen=True)
class TextOnScreen:
    """
    Text printed on screen.

    This class represents text that is positioned and rendered
    on the game screen. It handles text layout, positioning,
    and conversion to drawable elements.

    Arguments:
        `top_left`: The top-left coordinate of the text.

        `text`: The text object to render.

    Example:
        ```python
        from nextrpg.text_on_screen import TextOnScreen
        from nextrpg.text import Text
        from nextrpg.coordinate import Coordinate

        # Create text on screen
        text = Text("Hello, World!")
        position = Coordinate(100, 200)
        text_on_screen = TextOnScreen(top_left=position, text=text)
        ```
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

        Example:
            ```python
            # Get drawings for rendering
            drawings = text_on_screen.draw_on_screens
            ```
        """
        left, top = self.top_left
        return tuple(
            DrawOnScreen(
                Coordinate(left, top + height), Drawing(self._surface(line))
            )
            for line, height in zip(self.text.lines, self.text.line_heights)
        )

    def _surface(self, line: str) -> Surface:
        """
        Render a single line of text to a pygame surface.

        Arguments:
            `line`: The text line to render.

        Returns:
            `Surface`: The rendered text surface.
        """
        return self.text.config.font.pygame.render(
            line,
            self.text.config.antialias,
            self.text.config.color,
        )
