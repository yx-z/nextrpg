from dataclasses import dataclass, field
from functools import cached_property

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.draw.group import DrawRelativeTo, Group
from nextrpg.draw.draw import Draw
from nextrpg.global_config.global_config import config
from nextrpg.global_config.text_config import TextConfig


@dataclass(frozen=True)
class Text:
    message: str
    config: TextConfig = field(default_factory=lambda: config().text)

    @cached_property
    def size(self) -> Size:
        text_sizes = tuple(
            self.config.font.text_size(line) for line in self._lines
        )
        width = max(s.width for s in text_sizes)
        height = sum(s.height for s in text_sizes)
        spacings = self.config.line_spacing * (len(self._lines) - 1)
        return Size(width, height + spacings)

    @cached_property
    def group(self) -> Group:
        leader = self._draw(self._lines[0])
        followers = tuple(
            DrawRelativeTo(self._draw(line), self._line_shift(i))
            for i, line in enumerate(self._lines[1:], start=1)
        )
        return Group(leader, followers)

    @cached_property
    def _lines(self) -> tuple[str, ...]:
        return tuple(self.message.splitlines())

    def _line_shift(self, index: int) -> Coordinate:
        height = self.config.font.text_height + self.config.line_spacing
        shift = height * index
        return Coordinate(0, shift)

    def _draw(self, line: str) -> Draw:
        surface = self.config.font.pygame.render(
            line, self.config.antialias, self.config.color
        )
        return Draw(surface)
