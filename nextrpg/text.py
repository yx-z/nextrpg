from dataclasses import dataclass, field
from functools import cached_property

from pygame import Surface

from nextrpg.config import TextConfig, config
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing


@dataclass
class Text:
    """
    Lines of text printed on screen.

    Arguments:
        `lines`: The lines of text to print.

        `top_left`: The top-left coordinate of the text.

        `config`: The text configuration.
    """

    lines: list[str]
    top_left: Coordinate
    config: TextConfig = field(default_factory=lambda: config().text)

    @cached_property
    def draw_on_screens(self) -> list[DrawOnScreen]:
        """
        The lines of text rendered on screen.

        Returns:
            `list[DrawOnScreen]`: The lines of text rendered on screen.
        """
        return [
            DrawOnScreen(
                self.top_left + self._line_offset(i),
                Drawing(self._render(line)),
            )
            for i, line in enumerate(self.lines)
        ]

    def _render(self, line: str) -> Surface:
        return self.config.font.pygame.render(
            line, antialias=self.config.antialias, color=self.config.color
        )

    def _line_offset(self, line_index: int) -> Coordinate:
        margin = self.config.margin
        return self.top_left + Coordinate(
            margin, margin + line_index * (margin + self.config.font.size)
        )
