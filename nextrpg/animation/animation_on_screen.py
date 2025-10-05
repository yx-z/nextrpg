from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.abstract_animation_on_screen import (
    AbstractAnimationOnScreen,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class AnimationOnScreen(AbstractAnimationOnScreen):
    coordinate: Coordinate
    animation: AnimationLike

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.animation.drawing_on_screens(self.coordinate)

    @override
    @property
    def is_complete(self) -> bool:
        return self.animation.is_complete

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        animation = self.animation.tick(time_delta)
        return replace(self, animation=animation)
