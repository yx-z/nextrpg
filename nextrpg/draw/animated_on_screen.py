from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from nextrpg.draw.draw import Draw
from nextrpg.draw.group import GroupOnScreen
from nextrpg.core.coordinate import Moving
from nextrpg.core.time import Millisecond
from nextrpg.draw.animated import Animated
from nextrpg.draw.draw import DrawOnScreen


class AnimatedOnScreen(ABC):
    @property
    @abstractmethod
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]: ...

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...


@dataclass(frozen=True)
class MovingAnimatedOnScreen(AnimatedOnScreen):
    moving: Moving
    animated: Animated

    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        res: list[DrawOnScreen] = []
        if isinstance(self.animated.draw, Draw):
            res.append(DrawOnScreen(self.moving.coordinate, self.animated.draw))
        else:
            group = GroupOnScreen(self.moving.coordinate, self.animated.draw)
            res += group.draw_on_screens
        return tuple(res)

    def tick(self, time_delta: Millisecond) -> Self:
        moving = self.moving.tick(time_delta)
        animated = self.animated.tick(time_delta)
        return replace(self, moving=moving, animated=animated)
