from abc import ABC

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent


class Scene(ABC):
    def tick(self, time_delta: Millisecond) -> Scene:
        return self

    @property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return ()

    def event(self, event: IoEvent) -> Scene:
        return self
