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
from nextrpg.geometry.directional_offset import DirectionalOffset
from nextrpg.geometry.size import Height, Size, Width

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
        drawing = tuple(d.drawing for d in self.line_drawing_and_heights)
        return DrawingGroup(drawing)

    @cached_property
    def line_drawing_and_heights(self) -> tuple[LineDrawingAndHeight, ...]:
        line_height = self.config.font.text_height + self.config.line_spacing
        res: list[LineDrawingAndHeight] = []
        for i, line in enumerate(self.lines):
            line_drawing = self._drawing(line) + i * line_height
            drawing_and_height = LineDrawingAndHeight(
                DrawingGroup(line_drawing), line_height
            )
            res.append(drawing_and_height)
        return tuple(res)

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
        self,
        other: (
            Coordinate
            | Width
            | Height
            | Size
            | DirectionalOffset
            | str
            | Text
            | Sprite
            | TextGroup
        ),
    ) -> ShiftedSprite | TextGroup:
        from nextrpg.drawing.text_group import TextGroup

        if isinstance(
            other, Coordinate | Width | Height | Size | DirectionalOffset
        ):
            return self.shift(other)

        if isinstance(other, TextGroup):
            texts = (self,) + other.text_or_sprites
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

    def _drawing(self, line: str) -> Drawing:
        surface = self.config.font.pygame.render(
            line, antialias=True, color=self.config.color.pygame
        )
        return Drawing(surface, allow_background_in_debug=False)


@dataclass(frozen=True)
class LineDrawingAndHeight:
    drawing: DrawingGroup
    height: Height
