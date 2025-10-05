from dataclasses import dataclass
from functools import cached_property

from typing import override

from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size


@dataclass(frozen=True)
class TextOnScreen(AnimationOnScreenLike):
    top_left: Coordinate
    text: Text | TextGroup

    @property
    def size(self) -> Size:
        return self.text.size

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.text.drawing_group.drawing_on_screens(self.top_left)

    @override
    @cached_property
    def drawing_on_screen(self) -> DrawingOnScreen:
        return DrawingOnScreens(self.drawing_on_screens).drawing_on_screen
