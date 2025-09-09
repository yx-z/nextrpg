from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.draw.drawing_on_screen import DrawingOnScreen


@dataclass(frozen=True, kw_only=True)
class Blur(TimedAnimationOnScreens):
    to_radius: int | float
    from_radius: int | float = 0

    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return tuple(
            drawing_on_screen.blur(self._radius)
            for drawing_on_screen in super().drawing_on_screens
        )

    @cached_property
    def _radius(self) -> float:
        return (
            self._timer.completed_percentage
            * (self.to_radius - self.from_radius)
            + self.from_radius
        )
