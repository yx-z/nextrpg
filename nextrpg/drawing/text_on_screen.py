from dataclasses import dataclass
from functools import cached_property

from nextrpg.drawing.abstract_animation_on_screen_like import (
    AbstractAnimationOnScreenLike,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class TextOnScreen(AbstractAnimationOnScreenLike):
    top_left_input: Coordinate
    text: Text | TextGroup

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.text.drawing.drawing_on_screens(self.top_left_input)
