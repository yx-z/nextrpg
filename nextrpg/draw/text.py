from __future__ import annotations

from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self

from nextrpg.config.config import config
from nextrpg.config.text_config import TextConfig
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.draw.relative_drawing import RelativeDrawing
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.draw.text_group import TextGroup


@dataclass(frozen=True)
class Text(Sizable):
    message: str
    config: TextConfig = field(default_factory=lambda: config().text)

    def __getitem__(self, s: slice) -> Self:
        return replace(self, message=self.message[s])

    @property
    def size(self) -> Size:
        return self.drawing_group.size

    @property
    def top_left(self) -> Coordinate:
        return self.drawing_group.top_left

    @cached_property
    def drawing_group(self) -> DrawingGroup:
        draws = tuple(
            RelativeDrawing(self._drawing(line), self._line_shift(i))
            for i, line in enumerate(self.lines)
        )
        return DrawingGroup(draws)

    @property
    def drawings(self) -> tuple[Drawing, ...]:
        return self.drawing_group.drawings

    def _drawing(self, line: str) -> Drawing:
        surface = self.config.font.pygame.render(
            line, self.config.smooth, self.config.color
        )
        return Drawing(surface, allow_background_in_debug=False)

    def __radd__(self, other: str) -> TextGroup:
        return self + other

    def __add__(self, other: str | Text | TextGroup) -> TextGroup:
        from nextrpg.draw.text_group import TextGroup

        if isinstance(other, TextGroup):
            return replace(other, texts=(self,) + other.texts)

        if isinstance(other, str):
            txt = replace(self, message=other)
        else:
            txt = other
        return TextGroup((self, txt))

    @cached_property
    def line_texts(self) -> tuple[Self, ...]:
        return tuple(self.text(l) for l in self.lines)

    def text(self, message: str) -> Self:
        return replace(self, message=message)

    @cached_property
    def lines(self) -> tuple[str, ...]:
        if not (wrap := self.config.wrap):
            return self.message.splitlines(keepends=True)

        # wrap lines
        lines: list[str] = []
        line_buffer: list[str] = []
        for line in self.message.splitlines(keepends=True):
            for word in line.split():
                joined = " ".join(line_buffer + [word])
                if self.config.font.text_size(joined).width <= wrap:
                    line_buffer.append(word)
                else:
                    if line_buffer:
                        lines.append(" ".join(line_buffer))
                    line_buffer = [word]
            if line_buffer:
                lines.append(" ".join(line_buffer))
                line_buffer = []
        return tuple(lines)

    def _line_shift(self, index: int) -> Size:
        height = self.config.font.text_height + self.config.line_spacing
        return (height * index).with_width(0)
