from abc import ABC, abstractmethod
from functools import cached_property
from typing import Self, TypeVar

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.sizable import Sizable


class AnimationOnScreen(Sizable, ABC):
    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    def tick(self, time_delta: Millisecond) -> Self:
        if self.is_complete:
            return self
        return self.tick_before_complete(time_delta)

    @abstractmethod
    def tick_before_complete(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def is_complete(self) -> bool: ...

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    @cached_property
    def _sized(self) -> DrawingOnScreens:
        return DrawingOnScreens(self.drawing_on_screens)


_AnimationOnScreen = TypeVar("_AnimationOnScreen", bound=AnimationOnScreen)


def tick_optional(
    animation: _AnimationOnScreen | None, time_delta: Millisecond
) -> _AnimationOnScreen | None:
    if animation:
        return animation.tick(time_delta)
    return None
