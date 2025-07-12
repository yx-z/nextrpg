from dataclasses import dataclass
from functools import cached_property

from pygame import Surface

from nextrpg.draw.coordinate import Coordinate
from nextrpg.draw.draw_on_screen import DrawOnScreen, Drawing
from nextrpg.draw.text import Text


@dataclass(frozen=True)
class TextOnScreen:
    """
    Text printed on screen.

    Arguments:
        `top_left`: The top-left coordinate of the text.
    """

    text: Text
    top_left: Coordinate

    @cached_property
    def draw_on_screen(self) -> tuple[DrawOnScreen, ...]:
        """
        The text rendered on screen.

        Returns:
            `DrawOnScreen`: The text rendered on screen.
        """
        left, top = self.top_left
        return tuple(
            DrawOnScreen(
                Coordinate(left, top + height), Drawing(self._surface(line))
            )
            for line, height in zip(self.text.lines, self.text.line_heights)
        )

    def _surface(self, line: str) -> Surface:
        return self.text.config.font.pygame.render(
            line,
            self.text.config.antialias,
            self.text.config.color,
        )
