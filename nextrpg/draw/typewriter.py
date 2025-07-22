from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.core.model import not_constructor_below
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.draw.animated import Animated


@dataclass(frozen=True)
class Typewriter(Animated):
    text_on_screen: TextOnScreen
    delay: Millisecond
    _: KW_ONLY = not_constructor_below()
    _index: int = 0
    _elapsed: Millisecond = 0

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        index = min(len(self.text_on_screen.text.message), self._index + 1)
        message = self.text_on_screen.text.message[:index]
        text = replace(self.text_on_screen.text, message=message)
        return replace(self.text_on_screen, text=text).draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        elapsed = self._elapsed + time_delta
        steps = elapsed // self.delay
        index = self._tick(steps)
        return replace(self, _index=index, _elapsed=elapsed % self.delay)

    def _tick(self, steps: int) -> int:
        message = self.text_on_screen.text.message
        index = self._index + 1
        for _ in range(steps):
            print(f"{index=} {len(message)=}")
            if index == len(message):
                break
            while index < len(message) and message[index].isspace():
                index += 1
        return index
