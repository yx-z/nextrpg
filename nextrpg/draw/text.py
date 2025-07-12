from dataclasses import dataclass, field
from functools import cached_property

from nextrpg.config import TextConfig, config
from nextrpg.core import Pixel, Size


@dataclass(frozen=True)
class Text:
    message: str
    config: TextConfig = field(default_factory=lambda: config().text)

    @cached_property
    def size(self) -> Size:
        if not self.message:
            return Size(0, 0)
        text_sizes = [self.config.font.text_size(line) for line in self.lines]
        width = max(s.width for s in text_sizes)
        height = sum(s.height for s in text_sizes)
        spacings = self.config.line_spacing * (len(self.lines) - 1)
        return Size(width, height + spacings)

    @cached_property
    def line_heights(self) -> list[Pixel]:
        return [
            (self.config.font.text_height + self.config.line_spacing) * i
            for i in range(len(self.lines))
        ]

    @cached_property
    def lines(self) -> list[str]:
        return self.message.splitlines()
