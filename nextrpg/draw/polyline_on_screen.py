from dataclasses import dataclass
from functools import cached_property

from nextrpg.core.color import Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Pixel
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.polygon_drawing import get_bounding_rectangle_area_on_screen
from nextrpg.draw.polyline_drawing import PolylineDrawing
from nextrpg.draw.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass(frozen=True)
class PolylineOnScreen:
    points: tuple[Coordinate, ...]

    @cached_property
    def length(self) -> Pixel:
        shifted = self.points[1:] + (self.points[0],)
        return sum(p.distance(np) for p, np in zip(self.points, shifted))

    def fill(
        self, color: Color, allow_background_in_debug: bool = True
    ) -> DrawingOnScreen:
        drawing = PolylineDrawing(
            self.points,
            color,
            allow_background_in_debug,
            self._bounding_rectangle_area_on_screen,
        )
        return DrawingOnScreen(
            self._bounding_rectangle_area_on_screen.top_left, drawing.drawing
        )

    @cached_property
    def _bounding_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        return get_bounding_rectangle_area_on_screen(self.points)
