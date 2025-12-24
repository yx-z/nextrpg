from collections.abc import Collection
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, override

from nextrpg.drawing.color import Color
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Height, Size, Width

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass(frozen=True)
class PolygonAreaOnScreen(AreaOnScreen):
    points: tuple[Coordinate, ...]

    @cached_property
    def top_left(self) -> Coordinate:
        return self._bounding_rectangle_area_on_screen.top_left

    @cached_property
    def size(self) -> Size:
        return self._bounding_rectangle_area_on_screen.size

    @override
    def fill(
        self, color: Color, allow_background_in_debug: bool = True
    ) -> DrawingOnScreen:
        from nextrpg.drawing.polygon_drawing import PolygonDrawing

        poly = PolygonDrawing(
            self.points,
            color,
            allow_background_in_debug,
            self._bounding_rectangle_area_on_screen,
        )
        return poly.drawing.drawing_on_screen(self.top_left)

    @override
    def collide(self, area: AreaOnScreen) -> bool:
        if isinstance(area, PolygonAreaOnScreen):
            poly = area
        else:
            poly = PolygonAreaOnScreen(area.points)

        for poly in (self, poly):
            for i in range(len(poly.points)):
                x1, y1 = poly.points[i]
                x2, y2 = poly.points[(i + 1) % len(poly.points)]
                axis = Coordinate(y1 - y2, x2 - x1)
                proj1 = _project_polygon(axis, self)
                proj2 = _project_polygon(axis, poly)
                if not _overlap(proj1, proj2):
                    return False
        return True

    @override
    def __contains__(self, other: Coordinate | AreaOnScreen) -> bool:
        if isinstance(other, AreaOnScreen):
            return all(c in self for c in other.points)

        inside = False
        px = other.left_value
        py = other.top_value
        points = self.points
        n = len(points)
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]
            if y1 == y2:
                continue
            if (y1 > py) != (y2 > py):
                x_intersect = (x2 - x1) * (py - y1) / (y2 - y1) + x1
                if px < x_intersect:
                    inside = not inside
        return inside

    @override
    def __add__(
        self, other: Coordinate | Size | Width | Height
    ) -> PolygonAreaOnScreen:
        points = tuple(p + other for p in self.points)
        return PolygonAreaOnScreen(points)

    @cached_property
    def _bounding_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        return get_bounding_rectangle_area_on_screen(self.points)


def get_bounding_rectangle_area_on_screen(
    points: Collection[Coordinate],
) -> RectangleAreaOnScreen:
    min_x = min(c.left for c in points)
    min_y = min(c.top for c in points)
    max_x = max(c.left for c in points)
    max_y = max(c.top for c in points)
    coordinate = min_x @ min_y
    # The bounding rectangle must have a size of at least (1, 1).
    # Otherwise, no surface to blit.
    # This is useful for drawing vertical/horizontal lines.
    width = max(max_x - min_x, Width(1))
    height = max(max_y - min_y, Height(1))
    size = width * height
    return coordinate.as_top_left_of(size).rectangle_area_on_screen


def _project_polygon(axis: Coordinate, poly: PolygonAreaOnScreen) -> Coordinate:
    dots = tuple(x * axis[0] + y * axis[1] for x, y in poly.points)
    return Coordinate(min(dots), max(dots))


def _overlap(coordinate1: Coordinate, coordinate2: Coordinate) -> bool:
    return not (
        coordinate1.top_value < coordinate2.left_value
        or coordinate2.top_value < coordinate1.left_value
    )
