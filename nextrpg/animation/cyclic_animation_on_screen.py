from dataclasses import dataclass

from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.animation.from_animation import FromAnimation
from nextrpg.draw.drawing_on_screen import DrawingOnScreen


@dataclass(frozen=True)
class CyclicAnimationOnScreen(FromAnimation):
    animation: CyclicAnimation

    @property
    def drawing_on_screen(self) -> DrawingOnScreen:
        return self.animation.drawing.drawing_on_screen(self.coordinate)
