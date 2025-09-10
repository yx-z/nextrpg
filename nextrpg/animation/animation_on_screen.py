from abc import ABC, abstractmethod
from functools import cached_property
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size


class AnimationOnScreen(AnimationOnScreenLike, ABC):
    @property
    def drawing_on_screen(self) -> DrawingOnScreen:
        return self._sized.drawing_on_screen

    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    def tick(self, time_delta: Millisecond) -> Self:
        if self.is_complete:
            return self
        return self._tick_before_complete(time_delta)

    @property
    @abstractmethod
    def is_complete(self) -> bool: ...

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    @abstractmethod
    def _tick_before_complete(self, time_delta: Millisecond) -> Self: ...

    @cached_property
    def _sized(self) -> DrawingOnScreens:
        return DrawingOnScreens(self.drawing_on_screens)


def tick_optional(
    animation: AnimationOnScreenLike | None, time_delta: Millisecond
) -> AnimationOnScreenLike | None:
    if animation:
        return animation.tick(time_delta)
    return None
