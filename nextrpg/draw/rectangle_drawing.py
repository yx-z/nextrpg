from __future__ import annotations

from typing import Any

from pygame import Rect, SRCALPHA, Surface
from pygame.draw import rect

from nextrpg.core.color import Color
from nextrpg.core.coordinate import ORIGIN
from nextrpg.core.dimension import Pixel, Size
from nextrpg.draw.transparent_drawing import TransparentDrawing


class RectangleDrawing(TransparentDrawing):
    border_radius: Pixel

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RectangleDrawing):
            return False
        return (
            self.size == other.size
            and self.color == other.color
            and self.border_radius == other.border_radius
        )

    def __init__(
        self, size: Size, color: Color, border_radius: Pixel | None = None
    ) -> None:
        surface = Surface(size, SRCALPHA)
        rectangle = Rect(ORIGIN, size)
        rect(surface, color, rectangle, border_radius=border_radius or -1)
        # Drawing
        object.__setattr__(self, "resource", surface)
        object.__setattr__(self, "color_key", None)
        object.__setattr__(self, "convert_alpha", None)
        object.__setattr__(self, "allow_background_in_debug", True)
        # TransparentDrawing
        object.__setattr__(self, "color", color)
        # RectangleDrawing
        object.__setattr__(self, "border_radius", border_radius)
