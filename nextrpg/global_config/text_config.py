from dataclasses import dataclass, replace
from typing import Self

from nextrpg.core.color import WHITE, Rgb, Rgba
from nextrpg.core.dimension import Pixel
from nextrpg.draw.font import Font


@dataclass(frozen=True)
class TextConfig:
    font: Font = Font(28)
    color: Rgba | Rgb = WHITE
    line_spacing: Pixel = 8
    anti_alias: bool = True
    auto_wrap: Pixel | None = None

    def spacing(self, line_spacing: Pixel) -> Self:
        return replace(self, line_spacing=line_spacing)

    def wrapped(self, auto_wrap: Pixel) -> Self:
        return replace(self, auto_wrap=auto_wrap)

    def sized(self, size: Pixel) -> Self:
        font = replace(self.font, size=size)
        return replace(self, font=font)

    def colored(self, color: Rgba | Rgb) -> Self:
        return replace(self, color=color)

    def scripted(self, script: str) -> Self:
        font = replace(self.font, script=script)
        return replace(self, font=font)

    @property
    def anti_aliased(self) -> Self:
        return replace(self, anti_alias=True)

    @property
    def non_anti_aliased(self) -> Self:
        return replace(self, anti_alias=False)

    @property
    def italic(self) -> Self:
        font = replace(self.font, italic=True)
        return replace(self, font=font)

    @property
    def non_italic(self) -> Self:
        font = replace(self.font, italic=False)
        return replace(self, font=font)

    @property
    def bold(self) -> Self:
        font = replace(self.font, bold=True)
        return replace(self, font=font)

    @property
    def non_bold(self) -> Self:
        font = replace(self.font, bold=False)
        return replace(self, font=font)

    @property
    def underline(self) -> Self:
        font = replace(self.font, underline=True)
        return replace(self, font=font)

    @property
    def non_underline(self) -> Self:
        font = replace(self.font, underline=False)
        return replace(self, font=font)

    @property
    def strike_through(self) -> Self:
        font = replace(self.font, strike_through=True)
        return replace(self, font=font)

    @property
    def non_strike_through(self) -> Self:
        font = replace(self.font, strike_through=False)
        return replace(self, font=font)
