from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Hashable

from pygame import SRCALPHA, Rect, Surface
from pygame.draw import rect

from nextrpg.core.color import Color
from nextrpg.core.coordinate import ORIGIN
from nextrpg.core.dimension import Pixel, Size
from nextrpg.draw.transparent_drawing import TransparentDrawing


@dataclass(frozen=True)
class RectangleDrawing:
    size: Size
    color: Color
    border_radius: Pixel | None = None
    allow_background_in_debug: bool = True
    tags: tuple[Hashable, ...] = ()

    @cached_property
    def drawing(self) -> TransparentDrawing:
        surface = Surface(self.size, SRCALPHA)
        rectangle = Rect(ORIGIN, self.size)
        rect(
            surface,
            self.color,
            rectangle,
            border_radius=self.border_radius or -1,
        )
        return TransparentDrawing(
            resource=surface,
            allow_background_in_debug=self.allow_background_in_debug,
            tags=self.tags,
            color=self.color,
        )
