from dataclasses import astuple, dataclass
from pathlib import Path

from pygame import Surface, image

from nextrpg.common_types import Coordinate, Size


@dataclass(frozen=True)
class Drawable:
    surface: Surface
    coordinate: Coordinate

    @property
    def size(self) -> Size:
        return Size(width=self.surface.width, height=self.surface.height)

    @property
    def pygame(self) -> tuple[Surface, tuple[int, int]]:
        return self.surface, astuple(self.coordinate)


def load(path: Path, coordinate: Coordinate) -> Drawable:
    return Drawable(surface=image.load(path), coordinate=coordinate)
