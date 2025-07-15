from dataclasses import dataclass

from nextrpg.model import export
from nextrpg.core import Pixel


@export
@dataclass(frozen=True)
class DrawOnScreenConfig:
    stroke_width: Pixel = 2
