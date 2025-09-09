from dataclasses import dataclass
from functools import cached_property

from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.sizable import Sizable


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
