from abc import ABC, abstractmethod
from typing import Self, override

from nextrpg.core.time import Millisecond
from nextrpg.drawing.abstract_animation_on_screen_like import (
    AbstractAnimationOnScreenLike,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen


class AbstractAnimationOnScreen(AbstractAnimationOnScreenLike, ABC):
    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self.is_complete:
            return self
        return self._tick_before_complete(time_delta)

    @property
    @abstractmethod
    def is_complete(self) -> bool: ...

    @abstractmethod
    def _tick_before_complete(self, time_delta: Millisecond) -> Self: ...
