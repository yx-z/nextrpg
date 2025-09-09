from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.text_on_screen import TextOnScreen


@dataclass_with_default(frozen=True)
class Typewriter(AnimationOnScreen):
    text_on_screen: TextOnScreen
    delay: Millisecond
    _: KW_ONLY = private_init_below()
    _index: int = 0
    _timer_per_character: Timer = default(lambda self: Timer(self.delay))

    @cached_property
    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        text = self.text_on_screen.text[: self._index + 1]
        return replace(self.text_on_screen, text=text).drawing_on_screens

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        if not (
            timer := self._timer_per_character.tick(time_delta)
        ).is_complete:
            return replace(self, _timer_per_character=timer)
        index = self._index + timer.elapsed // self.delay
        return replace(self, _index=index, _timer_per_character=timer.modulo)

    @override
    @property
    def is_complete(self) -> bool:
        num_chars = len(self.text_on_screen.text)
        return (
            self._index >= num_chars and self._timer_per_character.is_complete
        )
