from dataclasses import dataclass

from nextrpg.core.dimension import Pixel


@dataclass(frozen=True)
class DrawOnScreenConfig:
    stroke_thickness: Pixel = 2
