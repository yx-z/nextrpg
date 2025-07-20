from typing import Self

from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.core.time import Millisecond


class Typewriter:
    text: TextOnScreen

    @property
    def draw_on_screen(self) -> TextOnScreen:
        return self.text

    def tick(self, time_delta: Millisecond) -> Self:
        return self
