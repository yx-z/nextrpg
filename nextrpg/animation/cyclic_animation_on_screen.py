from dataclasses import dataclass
from functools import cached_property

from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.animation.from_animation import FromAnimation
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.drawing_on_screens import DrawingOnScreens


@dataclass(frozen=True)
class CyclicAnimationOnScreen(FromAnimation):
    animation: CyclicAnimation

    @cached_property
    def drawing_on_screen(self) -> DrawingOnScreen:
        drawing = self.animation.drawing
        if isinstance(drawing, DrawingGroup):
            drawings = drawing.drawing_on_screens(self.coordinate)
            return DrawingOnScreens(drawings).merge
        return drawing.drawing_on_screen(self.coordinate)
