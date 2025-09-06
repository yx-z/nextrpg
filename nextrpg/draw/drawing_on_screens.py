from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from pygame import SRCALPHA, Surface

from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.sizable import Sizable


@dataclass(frozen=True)
class DrawingOnScreens(Sizable):
    drawing_on_screens: tuple[DrawingOnScreen, ...]

    @cached_property
    def merge(self) -> DrawingOnScreen:
        surface = Surface(self.size, SRCALPHA)
        surfaces = tuple(
            (drawing_on_screen - self.top_left).pygame
            for drawing_on_screen in self.drawing_on_screens
        )
        surface.blits(surfaces)
        drawing = Drawing(surface)
        return DrawingOnScreen(self.top_left, drawing)

    @cached_property
    def top_left(self) -> Coordinate:
        min_left = min(d.top_left.left_value for d in self.drawing_on_screens)
        min_top = min(d.top_left.top_value for d in self.drawing_on_screens)
        return Coordinate(min_left, min_top)

    @cached_property
    def size(self) -> Size:
        min_left = min(d.top_left.left for d in self.drawing_on_screens)
        min_top = min(d.top_left.top for d in self.drawing_on_screens)
        max_left = max(d.bottom_right.left for d in self.drawing_on_screens)
        max_top = max(d.bottom_right.top for d in self.drawing_on_screens)
        width = max_left - min_left
        height = max_top - min_top
        return width * height
