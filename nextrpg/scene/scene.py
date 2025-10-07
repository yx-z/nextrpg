from abc import ABC, abstractmethod

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent


class Scene(ABC):
    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    def tick(self, time_delta: Millisecond) -> Scene:
        return self

    def event(self, event: IoEvent) -> Scene:
        return self
