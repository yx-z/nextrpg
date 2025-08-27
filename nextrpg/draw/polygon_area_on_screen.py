from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, override

from pygame import Mask
from pygame.mask import from_surface

from nextrpg.core.color import BLACK, Color
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Height, Size, Width
from nextrpg.draw.area_on_screen import AreaOnScreen
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.polygon_drawing import (
    PolygonDrawing,
    get_bounding_rectangle_area_on_screen,
)

if TYPE_CHECKING:
    from nextrpg.draw.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass(frozen=True)
class PolygonAreaOnScreen(AreaOnScreen):
    points: tuple[Coordinate, ...]
    bounding_rectangle_area_on_screen_input: RectangleAreaOnScreen | None = None

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
        drawing = PolygonDrawing(
            self.points,
            color,
            allow_background_in_debug,
            self._bounding_rectangle_area_on_screen,
        )
        return DrawingOnScreen(self.top_left, drawing.drawing)

    @override
    def collide(self, area: AreaOnScreen) -> bool:
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
        if self.bounding_rectangle_area_on_screen_input:
            return self.bounding_rectangle_area_on_screen_input
        return get_bounding_rectangle_area_on_screen(self.points)
