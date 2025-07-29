from dataclasses import dataclass
from functools import cached_property

from nextrpg.core.coordinate import Coordinate
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.text import Text


@dataclass(frozen=True)
class TextOnScreen:
    top_left: Coordinate
    text: Text

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self.text.group.draw_on_screens(self.top_left)
