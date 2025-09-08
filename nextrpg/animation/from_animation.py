from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation import Animation
from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class FromAnimation(AnimationOnScreen):
    coordinate: Coordinate
    animation: Animation

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.animation.drawing, Drawing):
            return (DrawingOnScreen(self.coordinate, self.animation.drawing),)
        return self.animation.drawing.drawing_on_screens(self.coordinate)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        animation = self.animation.tick(time_delta)
        return replace(self, animation=animation)

    @override
    @property
    def is_complete(self) -> bool:
        return self.animation.is_complete
