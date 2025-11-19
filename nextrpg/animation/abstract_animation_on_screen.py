from abc import ABC, abstractmethod
from typing import Self, override

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)


class AbstractAnimationOnScreen(SpriteOnScreen, ABC):
    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self.is_complete:
            return self
        return self._tick_before_complete(time_delta)

    @override
    @property
    @abstractmethod
    def is_complete(self) -> bool: ...

    @abstractmethod
    def _tick_before_complete(self, time_delta: Millisecond) -> Self: ...
