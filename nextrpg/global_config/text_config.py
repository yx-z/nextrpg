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

    def sized(self, size: Pixel) -> Self:
        font = replace(self.font, size=size)
        return replace(self, font=font)

    def colored(self, color: Rgba | Rgb) -> Self:
        return replace(self, color=color)
