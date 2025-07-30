from dataclasses import dataclass

from nextrpg.core.dimension import Pixel


@dataclass(frozen=True)
class TextGroupConfig:
    margin: Pixel = 0
    auto_wrap: Pixel | None = None
