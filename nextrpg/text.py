from dataclasses import dataclass, field
from functools import cached_property

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
        font = SysFont(self.config.font.name, self.config.font.size)
        return [
            DrawOnScreen(
                self.top_left + Coordinate(0, i * self.config.margin),
                Drawing(font.render(line, True, self.config.font.color)),
            )
            for i, line in enumerate(self.lines)
        ]
