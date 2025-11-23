from dataclasses import dataclass
from functools import cached_property
from typing import override

from pygame import SRCALPHA, Surface

from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Size


@dataclass(frozen=True)
class DrawingOnScreens(SpriteOnScreen):
    drawing_on_screens: tuple[DrawingOnScreen, ...]

    @override
    @cached_property
    def drawing_on_screen(self) -> DrawingOnScreen:
        if len(self.drawing_on_screens) == 1:
            return self.drawing_on_screens[0]
        surface = Surface(self.size, SRCALPHA).convert_alpha()
        surface.blits(
            (d - self.top_left).pygame for d in self.drawing_on_screens
        )
        drawing = Drawing(surface)
        return drawing.drawing_on_screen(self.top_left)

    @override
    @cached_property
    def top_left(self) -> Coordinate:
        min_left = min(d.top_left.left for d in self.drawing_on_screens)
        min_top = min(d.top_left.top for d in self.drawing_on_screens)
        return min_left @ min_top

    @cached_property
    def size(self) -> Size:
        max_left = max(d.bottom_right.left for d in self.drawing_on_screens)
        max_top = max(d.bottom_right.top for d in self.drawing_on_screens)
        width = max_left - self.top_left.left
        height = max_top - self.top_left.top
        return width * height

    @override
    @cached_property
    def is_complete(self) -> bool:
        return True
