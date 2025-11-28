from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, overload, override

from nextrpg.config.config import config
from nextrpg.config.drawing.text_group_config import TextGroupConfig
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.shifted_sprite import ShiftedSprite
from nextrpg.drawing.sprite import Sprite
from nextrpg.drawing.text import LineDrawingAndHeight, Text
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.directional_offset import DirectionalOffset
from nextrpg.geometry.size import ZERO_HEIGHT, ZERO_WIDTH, Height, Size, Width

if TYPE_CHECKING:
    from nextrpg.drawing.text_on_screen import TextOnScreen


@dataclass(frozen=True)
class TextGroup(Sprite):
    resource: str | Text | Sprite | tuple[str | Text | Sprite, ...]
    config: TextGroupConfig = field(
        default_factory=lambda: config().drawing.text_group
    )

    @cached_property
    def text_or_sprites(self) -> tuple[Text | Sprite, ...]:
        if isinstance(self.resource, str | Text | Sprite):
            return (_text_or_sprite(self.resource),)
        return tuple(_text_or_sprite(resource) for resource in self.resource)

    def __len__(self) -> int:
        return sum(
            len(text) if isinstance(text, str | Text) else 1
            for text in self.text_or_sprites
        )

    def text_on_screen(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> TextOnScreen:
        from nextrpg.drawing.text_on_screen import TextOnScreen

        return TextOnScreen(coordinate, self, anchor)

    def __getitem__(self, item: slice) -> Self:
        assert item.step in (
            None,
            1,
        ), f"TextGroup slicing only supports step=1 | None. Got {item.step}"

        res: list[Text | Sprite] = []
        start = item.start or 0
        idx = 0
        for text_or_sprite in self.text_or_sprites:
            if item.stop is not None and idx >= item.stop:
                break
            if isinstance(text_or_sprite, Text):
                msg_len = len(text_or_sprite.message)
            else:
                msg_len = 1
            if isinstance(text_or_sprite, Text):
                local_start = max(start - idx, 0)
                if item.stop is None:
                    local_stop = msg_len
                else:
                    local_stop = max(item.stop - idx, 0)
                it = text_or_sprite[local_start:local_stop]
            else:
                it = text_or_sprite
            res.append(it)
            idx += msg_len
        return replace(self, resource=tuple(res))

    def __radd__(self, other: str) -> TextGroup:
        return self + other

    @overload
    def __add__(self, other: Coordinate | Size) -> ShiftedSprite: ...

    @overload
    def __add__(self, other: str | Text) -> TextGroup: ...

    @override
    def __add__(
        self,
        other: (
            Coordinate | Width | Height | Size | DirectionalOffset | str | Text
        ),
    ) -> ShiftedSprite | TextGroup:
        if isinstance(
            other, Coordinate | Width | Height | Size | DirectionalOffset
        ):
            return self.shift(other)
        texts = self.text_or_sprites + (_text_or_sprite(other),)
        return replace(self, resource=texts)

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        sprites = tuple(d.drawing for d in self.line_drawing_and_heights)
        return DrawingGroup(sprites)

    @cached_property
    def line_drawing_and_heights(self) -> tuple[LineDrawingAndHeight, ...]:
        lines = [[t] for t in _text_or_sprite_line(self._no_wrap[0])]
        for text_or_sprite in self._no_wrap[1:]:
            line = _text_or_sprite_line(text_or_sprite)
            # Concatenate the current line to the previous line so that
            # the text is continuous.
            lines[-1].append(line[0])
            lines += [[t] for t in line[1:]]

        res: list[LineDrawingAndHeight] = []
        curr_height = ZERO_HEIGHT
        for line in lines:
            curr_width = ZERO_WIDTH
            line_height = (
                max(sprite.height for sprite in line) + self.config.line_spacing
            )
            line_group: list[ShiftedSprite] = []
            for sprite in line:
                height_diff = line_height - sprite.height
                shift = curr_width * (curr_height + height_diff)
                line_group.append(sprite.drawing + shift)
                curr_width += sprite.width + self.config.margin
            drawing_group = DrawingGroup(tuple(line_group))
            line_res = LineDrawingAndHeight(drawing_group, line_height)
            res.append(line_res)
            curr_height += line_height
        return tuple(res)

    @cached_property
    def _no_wrap(self) -> tuple[Text | Sprite, ...]:
        return tuple(_no_wrap(t) for t in self.text_or_sprites)


def _no_wrap(text_or_sprite: Text | Sprite) -> Text | Sprite:
    if isinstance(text_or_sprite, Text):
        cfg = replace(text_or_sprite.config, wrap=None)
        return replace(text_or_sprite, config=cfg)
    return text_or_sprite


def _text_or_sprite(text_or_sprite: str | Text | Sprite) -> Text | Sprite:
    if isinstance(text_or_sprite, str):
        return Text(text_or_sprite)
    return text_or_sprite


def _text_or_sprite_line(
    text_or_sprite: Text | Sprite,
) -> tuple[Text | Sprite, ...]:
    if isinstance(text_or_sprite, Text):
        return text_or_sprite.line_texts
    return (text_or_sprite,)
