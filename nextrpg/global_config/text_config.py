from dataclasses import dataclass, replace
from typing import Self

from nextrpg.core.color import WHITE, Color
from nextrpg.core.dimension import Height, Pixel, Width
from nextrpg.draw.font import Font


@dataclass(frozen=True)
class TextConfig:
    font: Font = Font(28)
    color: Color = WHITE
    line_spacing: Height = Height(8)
    anti_alias: bool = True
    wrap: Width | None = None

    def line_spaced(self, line_spacing: Height) -> Self:
        return replace(self, line_spacing=line_spacing)

    def wrapped(self, wrap: Width) -> Self:
        return replace(self, wrap=wrap)

    def sized(self, size: Pixel) -> Self:
        return replace(self, font=self.font.sized(size))

    def colored(self, color: Color) -> Self:
        return replace(self, color=color)

    def scripted(self, script: str) -> Self:
        return replace(self, font=self.font.scripted(script))

    @property
    def italicized(self) -> Self:
        return replace(self, font=self.font.italicized)

    @property
    def bolded(self) -> Self:
        return replace(self, font=self.font.bolded)

    @property
    def underlined(self) -> Self:
        return replace(self, font=self.font.underlined)

    @property
    def strikethroughed(self) -> Self:
        return replace(self, font=self.font.strikethroughed)
