from functools import cached_property
from typing import Self, override

from nextrpg.core.coordinate import Coordinate
from nextrpg.draw.animation_on_screen import AnimationOnScreen
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.pygame_event import PygameEvent


class Scene(AnimationOnScreen):
    @property
    def drawing_on_screen_shift(self) -> Coordinate | None:
        return None

    @cached_property
    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if shift := self.drawing_on_screen_shift:
            return tuple(
                d.add_fast(shift) for d in self.drawing_on_screens_before_shift
            )
        return self.drawing_on_screens_before_shift

    @property
    def drawing_on_screens_before_shift(self) -> tuple[DrawingOnScreen, ...]:
        return ()

    def event(self, event: PygameEvent) -> Self:
        return self
