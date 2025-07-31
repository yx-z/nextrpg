from dataclasses import dataclass, replace
from typing import Self

from nextrpg.core.color import WHITE, Color
from nextrpg.core.dimension import Pixel
from nextrpg.draw.font import Font


@dataclass(frozen=True)
class TextConfig:
    font: Font = Font(28)
    color: Color = WHITE
    line_spacing: Pixel = 8
    anti_alias: bool = True
    wrap: Pixel | None = None

    def line_spaced(self, line_spacing: Pixel) -> Self:
        return replace(self, line_spacing=line_spacing)

    def wrapped(self, auto_wrap: Pixel) -> Self:
        return replace(self, auto_wrap=auto_wrap)

    def sized(self, size: Pixel) -> Self:
        font = replace(self.font, size=size)
        return replace(self, font=font)

    def colored(self, color: Color) -> Self:
        return replace(self, color=color)

    def scripted(self, script: str) -> Self:
        font = replace(self.font, script=script)
        return replace(self, font=font)

    @property
    def italicized(self) -> Self:
        font = replace(self.font, italic=True)
        return replace(self, font=font)

    @property
    def bolded(self) -> Self:
        font = replace(self.font, bold=True)
        return replace(self, font=font)

    @property
    def underlined(self) -> Self:
        font = replace(self.font, underline=True)
        return replace(self, font=font)

    @property
    def strikethroughed(self) -> Self:
        font = replace(self.font, strikethrough=True)
        return replace(self, font=font)
