from dataclasses import dataclass

from nextrpg.core.dimension import Pixel


@dataclass(frozen=True)
class DrawOnScreenConfig:
    stroke_width: Pixel = 2
