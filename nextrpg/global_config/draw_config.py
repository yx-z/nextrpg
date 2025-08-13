from dataclasses import dataclass

from nextrpg.core.dimension import Pixel


@dataclass(frozen=True)
class DrawConfig:
    stroke_thickness: Pixel = 2
    cache_size: int = 8
