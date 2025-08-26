from dataclasses import dataclass
from functools import cached_property

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizable import Sizable
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.text import Text
from nextrpg.draw.text_group import TextGroup


@dataclass(frozen=True)
class TextOnScreen(Sizable):
    top_left: Coordinate
    text: Text | TextGroup

    @property
    def size(self) -> Size:
        return self.text.size

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.text.drawing_group.drawing_on_screens(self.top_left)
