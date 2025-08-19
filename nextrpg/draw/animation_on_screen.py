from abc import ABC, abstractmethod
from functools import cached_property
from typing import Self

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.sizable import Sizable
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import DrawingOnScreen, SizableDrawOnScreens


class AnimationOnScreen(Sizable, ABC):
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
    def _sized(self) -> SizableDrawOnScreens:
        return SizableDrawOnScreens(self.drawing_on_screens)
