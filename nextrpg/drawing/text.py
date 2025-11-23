from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, overload, override

from nextrpg.config.config import config
from nextrpg.config.drawing.text_config import TextConfig
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.shifted_sprite import ShiftedSprite
from nextrpg.drawing.sprite import Sprite
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Size

if TYPE_CHECKING:
    from nextrpg.drawing.text_group import TextGroup
    from nextrpg.drawing.text_on_screen import TextOnScreen


@dataclass(frozen=True)
class Text(Sprite):
    message: str
    config: TextConfig = field(default_factory=lambda: config().drawing.text)

    def configured(self, text_config: TextConfig) -> Self:
        return replace(self, config=text_config)

    def __len__(self) -> int:
        return len(self.message)

    def __getitem__(self, s: slice) -> Self:
        return replace(self, message=self.message[s])

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        draws = tuple(
            self._drawing(line) + self._line_shift(i)
            for i, line in enumerate(self.lines)
        )
        return DrawingGroup(draws)

    def text_on_screen(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> TextOnScreen:
        from nextrpg.drawing.text_on_screen import TextOnScreen

        return TextOnScreen(coordinate, self, anchor)

    def __radd__(self, other: str) -> TextGroup:
        return self + other

    @overload
    def __add__(self, other: Coordinate | Size) -> ShiftedSprite: ...

    @overload
    def __add__(self, other: str | Text | TextGroup) -> TextGroup: ...

    @override
    def __add__(
        self, other: Coordinate | Size | str | Text | TextGroup
    ) -> ShiftedSprite | TextGroup:
        if isinstance(other, Coordinate | Size):
            return self.shift(other)

        from nextrpg.drawing.text_group import TextGroup

        if isinstance(other, TextGroup):
            texts = (self,) + other.texts
            return replace(other, texts=texts)

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
        return (height * index).with_zero_width

    def _drawing(self, line: str) -> Drawing:
        surface = self.config.font.pygame.render(
            line, antialias=True, color=self.config.color.pygame
        )
        return Drawing(surface, allow_background_in_debug=False)
