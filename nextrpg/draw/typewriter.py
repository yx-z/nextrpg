from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.animation_on_screen import AnimationOnScreen
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.text_on_screen import TextOnScreen


@dataclass_with_init(frozen=True)
class Typewriter(AnimationOnScreen):
    text_on_screen: TextOnScreen
    delay: Millisecond
    _: KW_ONLY = not_constructor_below()
    _index: int = 0
    _timer: Timer = default(lambda self: Timer(self.delay))

    @cached_property
    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        text = self.text_on_screen.text[: self._index + 1]
        return replace(self.text_on_screen, text=text).drawing_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        timer = self._timer.tick(time_delta)
        if not timer.complete:
            return replace(self, _timer=timer)

        index = self._index + timer.elapsed // self.delay
        return replace(self, _index=index, _timer=timer.modulo)
