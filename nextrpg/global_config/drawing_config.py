from dataclasses import dataclass

from nextrpg.core.dimension import Pixel


@dataclass(frozen=True, slots=True)
class DrawingConfig:
    stroke_thickness: Pixel = 1
    cache_size: int = 8
    smooth_scale: bool = True
    smooth_line: bool = True
