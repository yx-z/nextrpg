from __future__ import annotations

from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self

from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import Size, Width
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup, RelativeDrawing
from nextrpg.global_config.global_config import config
from nextrpg.global_config.text_config import TextConfig
from nextrpg.global_config.text_group_config import TextGroupConfig


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
        return ORIGIN

    @cached_property
    def drawing_group(self) -> DrawingGroup:
        draws = tuple(
            RelativeDrawing(self._drawing(line), self._line_shift(i))
            for i, line in enumerate(self.lines)
        )
        return DrawingGroup(draws)

    def _drawing(self, line: str) -> Drawing:
        surface = self.config.font.pygame.render(
            line, self.config.smooth, self.config.color
        )
        return Drawing(surface, allow_background_in_debug=False)

    def __radd__(self, other: str) -> TextGroup:
        return self + other

    def __add__(self, other: str | Text | TextGroup) -> TextGroup:
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
            return tuple(self.message.splitlines(keepends=True))

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
        shift = height * index
        return Size(0, shift.value)


@dataclass(frozen=True)
class TextGroup(Sizable):
    texts: tuple[Text, ...]
    config: TextGroupConfig = field(default_factory=lambda: config().text_group)

    def __getitem__(self, item: slice) -> Self:
        if item.step not in (None, 1):
            raise ValueError("TextGroup slicing only supports step=1")

        texts: list[Text] = []
        start = item.start or 0
        stop = item.stop
        i = 0
        for text in self.texts:
            msg_len = len(text.message)
            if stop is not None and i >= stop:
                break
            text_start = max(start - i, 0)
            if text_start < msg_len:
                text_stop = stop - i if stop is not None else msg_len
                texts.append(text[text_start:text_stop])
            i += msg_len
        return replace(self, texts=tuple(texts))

    def __radd__(self, other: str) -> TextGroup:
        return self + other

    def __add__(self, other: str | Text) -> TextGroup:
        if isinstance(other, str):
            txt = Text(other)
        else:
            txt = other
        return replace(self, texts=self.texts + (txt,))

    @property
    def top_left(self) -> Coordinate:
        return ORIGIN

    @property
    def size(self) -> Size:
        return self.drawing_group.size

    @cached_property
    def drawing_group(self) -> DrawingGroup:
        lines = [[t] for t in self._no_wrap[0].line_texts]
        for text in self._no_wrap[1:]:
            lines[-1].append(text.line_texts[0])
            lines += [[t] for t in text.line_texts[1:]]

        res: list[RelativeDrawing] = []
        curr_height = 0
        for line in lines:
            curr_width = 0
            line_height = max(word.height.value for word in line)
            for word in line:
                word_width, word_height = word.size
                height_diff = line_height - word_height
                shift = Size(curr_width, curr_height + height_diff)
                res.append(RelativeDrawing(word.drawing_group, shift))
                curr_width += word_width + self.config.margin.value
            curr_height += line_height + self.config.line_spacing.value
        return DrawingGroup(tuple(res))

    def _width(self, line: list[Text]) -> Width:
        widths = sum(t.size.width.value for t in line)
        margins = (len(line) - 1) * self.config.margin.value
        return Width(widths + margins)

    @cached_property
    def _no_wrap(self) -> tuple[Text, ...]:
        return tuple(_no_wrap(t) for t in self.texts)


def _no_wrap(text: Text) -> Text:
    cfg = replace(text.config, wrap=None)
    return replace(text, config=cfg)
