from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation import Animation
from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class FromAnimation(AnimationOnScreen):
    coordinate: Coordinate
    animation: Animation

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.animation.drawing.drawing_on_screens(self.coordinate)

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        animation = self.animation.tick_before_complete(time_delta)
        return replace(self, animation=animation)

    @override
    @property
    def is_complete(self) -> bool:
        return self.animation.is_complete
