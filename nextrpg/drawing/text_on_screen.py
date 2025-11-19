from dataclasses import dataclass
from functools import cached_property

from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class TextOnScreen(SpriteOnScreen):
    coordinate: Coordinate
    text: Text | TextGroup
    anchor: Anchor = Anchor.TOP_LEFT

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.text.drawing.drawing_on_screens(
            self.coordinate, self.anchor
        )
