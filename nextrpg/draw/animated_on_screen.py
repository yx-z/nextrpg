from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from nextrpg.core.coordinate import Coordinate, Moving
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.core.time import Millisecond
from nextrpg.draw.animated import Animated
from nextrpg.draw.draw import Draw, DrawOnScreen, SizedDrawOnScreens
from nextrpg.draw.group import GroupOnScreen


class AnimatedOnScreen(Sizeable, ABC):
    @property
    @abstractmethod
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]: ...

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    @cached_property
    def _sized(self) -> SizedDrawOnScreens:
        return SizedDrawOnScreens(self.draw_on_screens)


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
