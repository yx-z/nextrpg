from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, override

from pygame import Mask
from pygame.mask import from_surface

from nextrpg.core.area_on_screen import AreaOnScreen
from nextrpg.core.color import BLACK, Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Height, Size, Width

if TYPE_CHECKING:
    from nextrpg.core.rectangle_area_on_screen import RectangleAreaOnScreen
    from nextrpg.draw.drawing_on_screen import DrawingOnScreen


@dataclass(frozen=True)
class PolygonAreaOnScreen(AreaOnScreen):
    points: tuple[Coordinate, ...]

    @property
    def top_left(self) -> Coordinate:
        return self._bounding_rectangle_area_on_screen.top_left

    @property
    def size(self) -> Size:
        return self._bounding_rectangle_area_on_screen.size

    @override
    def fill(
        self, color: Color, allow_background_in_debug: bool = True
    ) -> DrawingOnScreen:
        from nextrpg.draw.polygon_drawing import PolygonDrawing
        from nextrpg.draw.drawing_on_screen import DrawingOnScreen

        drawing = PolygonDrawing(
            self.points,
            color,
            allow_background_in_debug,
            self._bounding_rectangle_area_on_screen,
        )
        return DrawingOnScreen(self.top_left, drawing.drawing)

    @override
    def collide(self, area: AreaOnScreen) -> bool:
        if isinstance(area, PolygonAreaOnScreen):
            poly = area
        else:
            poly = PolygonAreaOnScreen(area.points)

        if not self._bounding_rectangle_area_on_screen.collide(
            poly._bounding_rectangle_area_on_screen
        ):
            return False

        offset = (
            self._bounding_rectangle_area_on_screen.top_left
            - poly._bounding_rectangle_area_on_screen.top_left
        )
        return bool(self._mask.overlap(poly._mask, offset))

    @override
    def __contains__(self, coordinate: Coordinate) -> bool:
        x, y = coordinate - self._bounding_rectangle_area_on_screen.top_left
        width, height = self._mask.get_size()
        if 0 <= x < width and 0 <= y < height:
            return bool(self._mask.get_at((x, y)))
        return False

    @override
    def __add__(
        self, other: Coordinate | Size | Width | Height
    ) -> PolygonAreaOnScreen:
        points = tuple(p + other for p in self.points)
        return PolygonAreaOnScreen(points)

    @cached_property
    def _mask(self) -> Mask:
        surface = self.fill(BLACK).drawing.pygame
        return from_surface(surface)

    @cached_property
    def _bounding_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        return get_bounding_rectangle_area_on_screen(self.points)


def get_bounding_rectangle_area_on_screen(
    points: tuple[Coordinate, ...],
) -> RectangleAreaOnScreen:
    from nextrpg.core.rectangle_area_on_screen import RectangleAreaOnScreen

    min_x = min(c.left_value for c in points)
    min_y = min(c.top_value for c in points)
    max_x = max(c.left_value for c in points)
    max_y = max(c.top_value for c in points)
    coordinate = Coordinate(min_x, min_y)
    # The bounding rectangle must have a size of at least (1, 1).
    # Otherwise, no surface to blit.
    # This is useful for drawing vertical/horizontal lines.
    width = max(max_x - min_x, 1)
    height = max(max_y - min_y, 1)
    size = Size(width, height)
    return RectangleAreaOnScreen(coordinate, size)
