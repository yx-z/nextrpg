"""
Text interface.
"""

from dataclasses import dataclass, field
from functools import cached_property

from pygame import Surface

from nextrpg.config import TextConfig, config
from nextrpg.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.coordinate import Coordinate


@dataclass(frozen=True)
class Text:
    """
    Text printed on screen.

    Arguments:
        `message`: The text to print.

        `top_left`: The top-left coordinate of the text.

        `config`: The text configuration.
    """

    message: str
    top_left: Coordinate
    config: TextConfig = field(default_factory=lambda: config().text)

    @cached_property
    def draw_on_screen(self) -> DrawOnScreen:
        """
        The text rendered on screen.

        Returns:
            `DrawOnScreen`: The text rendered on screen.
        """
        return DrawOnScreen(self.top_left, Drawing(self._surface))

    @cached_property
    def _surface(self) -> Surface:
        return self.config.font.pygame.render(
            self.message,
            antialias=self.config.antialias,
            color=self.config.color,
        )
