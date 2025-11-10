from abc import ABC, abstractmethod
from re import A

from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent


class Scene(AnimationOnScreenLike, ABC):
    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Scene: ...

    def event(self, event: IoEvent) -> Scene:
        return self
