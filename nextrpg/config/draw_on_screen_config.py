from dataclasses import dataclass

from nextrpg.core import Pixel


@dataclass(frozen=True)
class DrawOnScreenConfig:
    stroke_width: Pixel = 2
