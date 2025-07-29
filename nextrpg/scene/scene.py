from functools import cached_property
from typing import Self, override

from nextrpg.core.coordinate import Coordinate
from nextrpg.draw.animated_on_screen import AnimatedOnScreen
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.event.pygame_event import PygameEvent


class Scene(AnimatedOnScreen):
    @property
    def draw_on_screen_shift(self) -> Coordinate | None:
        return None

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if shift := self.draw_on_screen_shift:
            return tuple(d + shift for d in self.draw_on_screens_before_shift)
        return self.draw_on_screens_before_shift

    @property
    def draw_on_screens_before_shift(self) -> tuple[DrawOnScreen, ...]:
        return ()

    def event(self, event: PygameEvent) -> Self:
        return self
