from dataclasses import dataclass

from nextrpg.geometry.dimension import Pixel


@dataclass(frozen=True)
class UiConfig:
    padding: Pixel = 8
