from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.core.time import Millisecond
from nextrpg.draw.color import Color
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.gui.area import screen
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class ViewOnlyScene(Scene):
    background: Color | DrawingOnScreen | AnimationOnScreen

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if isinstance(self.background, AnimationOnScreen):
            background = self.background.tick(time_delta)
        else:
            background = self.background
        return replace(self, background=background)

    @override
    @property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        match self.background:
            case Color():
                return (screen().fill(self.background),)
            case DrawingOnScreen():
                return (self.background,)
            case AnimationOnScreen():
                return self.background.drawing_on_screens
