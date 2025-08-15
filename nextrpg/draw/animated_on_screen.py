from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self

from nextrpg.core.coordinate import Coordinate, Moving
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.core.time import Millisecond
from nextrpg.draw.animated import Animated
from nextrpg.draw.drawing import Drawing, DrawingOnScreen, SizedDrawOnScreens
from nextrpg.draw.drawing_group import DrawingGroupOnScreen


class AnimatedOnScreen(Sizeable, ABC):
    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

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
        return SizedDrawOnScreens(self.drawing_on_screens)


@dataclass(frozen=True)
class MovingAnimatedOnScreen(AnimatedOnScreen):
    moving: Moving
    animated: Animated

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        res: list[DrawingOnScreen] = []
        if isinstance(self.animated.drawing, Drawing):
            res.append(
                DrawingOnScreen(self.moving.coordinate, self.animated.drawing)
            )
        else:
            group = DrawingGroupOnScreen(
                self.moving.coordinate, self.animated.drawing
            )
            res += group.drawing_on_screens
        return tuple(res)

    def tick(self, time_delta: Millisecond) -> Self:
        moving = self.moving.tick(time_delta)
        animated = self.animated.tick(time_delta)
        return replace(self, moving=moving, animated=animated)
