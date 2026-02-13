from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from nextrpg.drawing.color import WHITE, Color
from nextrpg.drawing.font import Font, FontSize
from nextrpg.geometry.size import Height, Width


@dataclass(frozen=True)
class TextConfig:
    font: Font = Font(FontSize(28))
    color: Color = WHITE
    line_spacing: Height = Height(8)
    wrap: Width | None = None

    def with_font(self, font: Font) -> Self:
        return replace(self, font=font)

    def with_line_spacing(self, line_spacing: Height) -> Self:
        return replace(self, line_spacing=line_spacing)

    def with_wrap(self, wrap: Width) -> Self:
        return replace(self, wrap=wrap)

    def with_font_size(self, height: Height) -> Self:
        font = self.font.with_font_size(FontSize(height.value))
        return replace(self, font=font)

    def with_color(self, color: Color) -> Self:
        return replace(self, color=color)

    def with_script(self, script: str) -> Self:
        font = self.font.with_script(script)
        return replace(self, font=font)

    @cached_property
    def italicized(self) -> Self:
        return replace(self, font=self.font.italicized)

    @cached_property
    def bolded(self) -> Self:
        return replace(self, font=self.font.bolded)

    @cached_property
    def underlined(self) -> Self:
        return replace(self, font=self.font.underlined)

    @cached_property
    def strikethroughed(self) -> Self:
        return replace(self, font=self.font.strikethroughed)
