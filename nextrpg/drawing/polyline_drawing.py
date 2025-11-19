from typing import override

from pygame import Surface
from pygame.draw import lines

from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.geometry.coordinate import Coordinate


class PolylineDrawing(PolygonDrawing):
    @override
    def _draw(self, surface: Surface, points: list[Coordinate]) -> None:
        lines(surface, self.color.pygame, closed=False, points=points)
