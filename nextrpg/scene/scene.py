from __future__ import annotations

from abc import abstractmethod
from functools import cached_property

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent
from nextrpg.geometry.coordinate import Coordinate


class Scene:
    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Scene: ...

    @property
    def drawing_on_screen_shift(self) -> Coordinate | None:
        return None

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if shift := self.drawing_on_screen_shift:
            return tuple(
                d.add_fast(shift) for d in self.drawing_on_screens_before_shift
            )
        return ()

    @property
    def drawing_on_screens_before_shift(self) -> tuple[DrawingOnScreen, ...]:
        return ()

    def event(self, event: IoEvent) -> Scene:
        return self
