from dataclasses import dataclass
from functools import cached_property

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.text import Text, TextGroup


@dataclass(frozen=True)
class TextOnScreen(Sizeable):
    top_left: Coordinate
    text: Text | TextGroup

    @property
    def size(self) -> Size:
        return self.text.size

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self.text.group.draw_on_screens(self.top_left)
