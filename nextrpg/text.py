from dataclasses import dataclass, field
from functools import cached_property

from pygame import Surface
from pygame.font import SysFont

from nextrpg.config import TextConfig, config
from nextrpg.draw_on_screen import Coordinate, DrawOnScreen, Drawing


@dataclass(frozen=True)
class Text:
    lines: list[str]
    top_left: Coordinate
    config: TextConfig = field(default_factory=lambda: config().text)

    @cached_property
    def draw_on_screens(self) -> list[DrawOnScreen]:
        margin = self.config.margin
        return [
            DrawOnScreen(
                self.top_left
                + Coordinate(margin, i * (margin + self.config.font.size)),
                Drawing(self._render(line)),
            )
            for i, line in enumerate(self.lines)
        ]

    def _render(self, line: str) -> Surface:
        return self._font.render(
            line, antialias=False, color=self.config.font.color
        )

    @cached_property
    def _font(self) -> SysFont:
        return SysFont(self.config.font.name, self.config.font.size)
