from typing import override

from pygame import Surface
from pygame.draw import lines

from nextrpg.core.coordinate import Coordinate
from nextrpg.draw.polygon_drawing import PolygonDrawing


class PolylineDrawing(PolygonDrawing):
    @override
    def _draw(self, surface: Surface, points: tuple[Coordinate, ...]) -> None:
        lines(surface, self.color, closed=False, points=points)
