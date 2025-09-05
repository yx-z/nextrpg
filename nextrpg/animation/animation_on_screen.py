from abc import ABC, abstractmethod
from functools import cached_property
from typing import Self, TypeVar

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.sizable_drawing_on_screens import SizableDrawingOnScreens
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.sizable import Sizable


class AnimationOnScreen(Sizable, ABC):
    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def complete(self) -> bool: ...

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    @cached_property
    def _sized(self) -> SizableDrawingOnScreens:
        return SizableDrawingOnScreens(self.drawing_on_screens)


_AnimationOnScreen = TypeVar("_AnimationOnScreen", bound=AnimationOnScreen)


def tick_optional(
    animation: _AnimationOnScreen | None, time_delta: Millisecond
) -> _AnimationOnScreen:
    if animation:
        return animation.tick(time_delta)
    return None
