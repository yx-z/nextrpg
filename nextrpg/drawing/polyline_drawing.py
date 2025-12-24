from dataclasses import dataclass
from typing import override

from pygame import Surface
from pygame.draw import lines

from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class PolylineDrawing(PolygonDrawing):
    closed: bool = False

    @override
    def _draw(self, surface: Surface, points: tuple[Coordinate, ...]) -> None:
        lines(surface, self.color.pygame, closed=self.closed, points=points)
