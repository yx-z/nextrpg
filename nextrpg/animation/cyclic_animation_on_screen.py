from dataclasses import dataclass
from functools import cached_property

from nextrpg.animation.animation_like_on_screen import AnimationLikeOnScreen
from nextrpg.animation.cyclic_animation import CyclicAnimation
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens


@dataclass(frozen=True)
class CyclicAnimationOnScreen(AnimationLikeOnScreen):
    animation: CyclicAnimation

    @cached_property
    def drawing_on_screen(self) -> DrawingOnScreen:
        drawing = self.animation.drawing
        if isinstance(drawing, DrawingGroup):
            drawings = drawing.drawing_on_screens(self.coordinate)
            return DrawingOnScreens(drawings).drawing_on_screen
        return drawing.drawing_on_screen(self.coordinate)
