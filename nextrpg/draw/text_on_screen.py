from dataclasses import dataclass
from functools import cached_property

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.draw.drawing import DrawingOnScreen
from nextrpg.draw.text import Text, TextGroup


@dataclass(frozen=True)
class TextOnScreen(Sizeable):
    top_left: Coordinate
    text: Text | TextGroup

    @property
    def size(self) -> Size:
        return self.text.size

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.text.group.drawing_on_screens(self.top_left)
