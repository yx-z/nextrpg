from dataclasses import dataclass

from nextrpg.core.dimension import Pixel


@dataclass(frozen=True)
class TextGroupConfig:
    line_spacing: Pixel = 8
    margin: Pixel = 2
    auto_wrap: Pixel | None = None
