from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Self

from nextrpg import Drawing
from nextrpg.core.coordinate import Moving
from nextrpg.core.time import Millisecond
from nextrpg.draw.animated import Animated
from nextrpg.draw.draw_on_screen import DrawOnScreen


class AnimatedOnScreen(ABC):
    @property
    @abstractmethod
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        """ """

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self:
        """ """


@dataclass(frozen=True)
class MovingAnimatedOnScreen(AnimatedOnScreen):
    moving: Moving
    animated: Animated

    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        res = []
        for d in self.animated.drawings:
            if isinstance(d, Drawing):
                res.append(DrawOnScreen(self.moving.coordinate, d))
            else:
                res += d.draw_on_screens(self.moving.coordinate)
        return tuple(res)

    def tick(self, time_delta: Millisecond) -> Self:
        moving = self.moving.tick(time_delta)
        animated = self.animated.tick(time_delta)
        return replace(self, moving=moving, animated=animated)
