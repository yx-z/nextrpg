from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from pygame import SRCALPHA, Rect, Surface
from pygame.draw import rect

from nextrpg.core.color import Color
from nextrpg.draw.drawing import Drawing
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.geometry.dimension import Pixel, Size


@dataclass(frozen=True)
class RectangleDrawing:
    size: Size
    color: Color
    border_radius: Pixel | None = None
    allow_background_in_debug: bool = True

    @cached_property
    def drawing(self) -> Drawing:
        surface = Surface(self.size, SRCALPHA)
        rectangle = Rect(ORIGIN, self.size)
        if self.border_radius is None:
            rect(surface, self.color, rectangle)
        else:
            rect(
                surface, self.color, rectangle, border_radius=self.border_radius
            )
        return Drawing(
            surface, allow_background_in_debug=self.allow_background_in_debug
        )
