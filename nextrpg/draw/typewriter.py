from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.core.model import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.animated import Animated
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.draw.text_on_screen import TextOnScreen


@dataclass_with_instance_init
class Typewriter(Animated):
    text_on_screen: TextOnScreen
    delay: Millisecond
    _: KW_ONLY = not_constructor_below()
    _index: int = 0
    _timer: Timer = instance_init(lambda self: Timer(self.delay))

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        index = min(len(self.text_on_screen.text.message), self._index + 1)
        message = self.text_on_screen.text.message[:index]
        text = replace(self.text_on_screen.text, message=message)
        return replace(self.text_on_screen, text=text).draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        timer = self._timer.tick(time_delta)
        if not timer.complete:
            return replace(self, _timer=timer)

        index = self._tick(timer.elapsed // self.delay)
        return replace(self, _index=index, _timer=timer.modulo)

    def _tick(self, steps: int) -> int:
        message = self.text_on_screen.text.message
        index = self._index + 1
        for _ in range(steps):
            if index == len(message):
                break
            while index < len(message) and message[index].isspace():
                index += 1
        return index
