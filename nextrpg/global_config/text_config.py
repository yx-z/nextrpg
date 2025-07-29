from dataclasses import dataclass

from nextrpg.core.dimension import Pixel
from nextrpg.core.color import WHITE, Rgba
from nextrpg.draw.font import Font


@dataclass(frozen=True)
class TextConfig:
    font: Font = Font(28)
    color: Rgba = WHITE
    line_spacing: Pixel = 8
    antialias: bool = True
