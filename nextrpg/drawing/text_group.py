from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self

from nextrpg.config.config import config
from nextrpg.config.text_group_config import TextGroupConfig
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.relative_drawing import RelativeDrawing
from nextrpg.drawing.text import Text
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Height, Size, Width
from nextrpg.geometry.sizable import Sizable

if TYPE_CHECKING:
    from nextrpg.drawing.text_on_screen import TextOnScreen


@dataclass(frozen=True)
class TextGroup(Sizable):
    texts: tuple[Text, ...]
    config: TextGroupConfig = field(default_factory=lambda: config().text_group)

    def __len__(self) -> int:
        return sum(len(text) for text in self.texts)

    def text_on_screen(self, coordinate: Coordinate) -> TextOnScreen:
        from nextrpg.drawing.text_on_screen import TextOnScreen

        return TextOnScreen(coordinate, self)

    @property
    def drawings(self) -> tuple[Drawing, ...]:
        return self.drawing_group.drawings

    def __getitem__(self, item: slice) -> Self:
        if item.step not in (None, 1):
            raise ValueError("TextGroup slicing only supports step=1")

        texts: list[Text] = []
        start = item.start or 0
        stop = item.stop
        idx = 0
        for text in self.texts:
            msg_len = len(text.message)
            if stop is not None and idx >= stop:
                break
            text_start = max(start - idx, 0)
            if text_start < msg_len:
                text_stop = stop - idx if stop is not None else msg_len
                texts.append(text[text_start:text_stop])
            idx += msg_len
        return replace(self, texts=tuple(texts))

    def __radd__(self, other: str) -> TextGroup:
        return self + other

    def __add__(self, other: str | Text) -> TextGroup:
        if isinstance(other, str):
            text = Text(other)
        else:
            text = other
        return replace(self, texts=self.texts + (text,))

    @property
    def top_left(self) -> Coordinate:
        return self.drawing_group.top_left

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
        curr_height = Height(0)
        for line in lines:
            curr_width = Width(0)
            line_height = max(word.height for word in line)
            for word in line:
                height_diff = line_height - word.height
                shift = curr_width * (curr_height + height_diff)
                res.append(word.drawing_group.shift(shift))
                curr_width += word.width + self.config.margin
            curr_height += line_height + self.config.line_spacing
        return DrawingGroup(tuple(res))

    def _width(self, line: list[Text]) -> Width:
        widths = sum(t.size.width for t in line)
        margins = (len(line) - 1) * self.config.margin
        return widths + margins

    @cached_property
    def _no_wrap(self) -> tuple[Text, ...]:
        return tuple(_no_wrap(t) for t in self.texts)


def _no_wrap(text: Text) -> Text:
    cfg = replace(text.config, wrap=None)
    return replace(text, config=cfg)
