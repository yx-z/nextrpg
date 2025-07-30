from __future__ import annotations

from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel, Size
from nextrpg.draw.draw import Draw
from nextrpg.draw.group import Group, RelativeDraw
from nextrpg.global_config.global_config import config
from nextrpg.global_config.text_config import TextConfig
from nextrpg.global_config.text_group_config import TextGroupConfig


@dataclass(frozen=True)
class Text:
    message: str
    config: TextConfig = field(default_factory=lambda: config().text)

    @cached_property
    def size(self) -> Size:
        return self.group.size

    @cached_property
    def group(self) -> Group:
        draws = tuple(
            RelativeDraw(self.draw(line), self._line_shift(i))
            for i, line in enumerate(self.lines)
        )
        return Group(draws)

    def draw(self, line: str) -> Draw:
        surface = self.config.font.pygame.render(
            line, self.config.antialias, self.config.color
        )
        return Draw(surface)

    def __radd__(self, other: str) -> TextGroup:
        return self + other

    def __add__(self, other: str | Text | TextGroup) -> TextGroup:
        if isinstance(other, TextGroup):
            return replace(other, texts=(self,) + other.texts)

        cfg = replace(config().text_group, auto_wrap=self.config.auto_wrap)
        if isinstance(other, str):
            txt = replace(self, message=other)
        else:
            txt = other
        return TextGroup((self, txt), cfg)

    @cached_property
    def line_texts(self) -> tuple[Self, ...]:
        return tuple(self.text(l) for l in self.lines)

    def text(self, message: str) -> Self:
        return replace(self, message=message)

    @cached_property
    def lines(self) -> tuple[str, ...]:
        if not (wrap := self.config.auto_wrap):
            # split("\n") retains last new line as empty line
            # whereas splitlines() doesn't.
            return tuple(self.message.split("\n"))

        # wrap lines
        lines: list[str] = []
        line_buffer: list[str] = []
        for line in self.message.split("\n"):
            for word in line.split(" "):
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

    def _line_shift(self, index: int) -> Coordinate:
        height = self.config.font.text_height + self.config.line_spacing
        shift = height * index
        return Coordinate(0, shift)


@dataclass(frozen=True)
class TextGroup:
    texts: tuple[Text, ...]
    config: TextGroupConfig = field(default_factory=lambda: config().text_group)

    def __radd__(self, other: str) -> TextGroup:
        return self + other

    def __add__(self, other: str | Text) -> TextGroup:
        if isinstance(other, str):
            txt = Text(other)
        else:
            txt = other
        return replace(self, texts=self.texts + (txt,))

    @cached_property
    def group(self) -> Group:
        lines = [[t] for t in self._texts[0].line_texts]
        if wrap := self.config.auto_wrap:
            self._build_wrap_lines(lines, wrap)
        else:
            for text in self._texts[1:]:
                lines[-1].append(text.line_texts[0])
                lines += [[t] for t in text.line_texts[1:]]

        res: list[RelativeDraw] = []
        return Group(tuple(res))

    def _width(self, line: list[Text]) -> Pixel:
        widths = sum(t.size.width for t in line)
        margins = (len(line) - 1) * self.config.margin
        return widths + margins

    @cached_property
    def _texts(self) -> tuple[Text, ...]:
        return tuple(_no_wrap(t) for t in self.texts)

    def _build_wrap_lines(self, lines: list[list[Text]], wrap: Pixel) -> None:
        for text in self._texts[1:]:
            line_buffer = lines[-1]
            for line_text in text.line_texts:
                for word in line_text.message.split(" "):
                    word_text = line_text.text(word)
                    if (
                        line_buffer
                        and line_buffer[-1].config == word_text.config
                    ):
                        joined = f"{line_buffer[-1].message} {word}"
                        joined_lines = line_buffer[:-1] + [
                            word_text.text(joined)
                        ]
                    else:
                        joined_lines = line_buffer + [word_text]

                    if self._width(joined_lines) <= wrap:
                        line_buffer = joined_lines
                    else:
                        lines.append(line_buffer)
                        line_buffer = [word_text]
                if line_buffer:
                    lines.append(line_buffer)
                    line_buffer = []


def _no_wrap(text: Text) -> Text:
    cfg = replace(text.config, auto_wrap=None)
    return replace(text, config=cfg)
