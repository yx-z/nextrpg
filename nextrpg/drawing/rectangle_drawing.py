from dataclasses import dataclass
from functools import cached_property

from pygame.constants import SRCALPHA
from pygame.draw import rect
from pygame.rect import Rect
from pygame.surface import Surface

from nextrpg.drawing.color import Color
from nextrpg.drawing.drawing import Drawing
from nextrpg.geometry.coordinate import ORIGIN
from nextrpg.geometry.dimension import Pixel, Size


@dataclass(frozen=True)
class RectangleDrawing:
    size: Size
    color: Color
    width: Pixel = 0
    border_radius: Pixel = -1
    allow_background_in_debug: bool = True

    @cached_property
    def drawing(self) -> Drawing:
        surface = Surface(self.size, SRCALPHA)
        rectangle = Rect(ORIGIN, self.size)
        rect(
            surface,
            self.color,
            rectangle,
            self.width,
            self.border_radius,
        )
        return Drawing(
            surface, allow_background_in_debug=self.allow_background_in_debug
        )
