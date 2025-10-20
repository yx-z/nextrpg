from typing import override

from pygame.draw import lines
from pygame.surface import Surface

from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.geometry.coordinate import Coordinate


class PolylineDrawing(PolygonDrawing):
    @override
    def _draw(self, surface: Surface, points: tuple[Coordinate, ...]) -> None:
        lines(surface, self.color, closed=False, points=points)
