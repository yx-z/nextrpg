from dataclasses import dataclass, field, replace
from typing import Self

from nextrpg.config.config import config
from nextrpg.core import Millisecond, alpha_from_percentage
from nextrpg.draw.draw_on_screen import DrawOnScreen


@dataclass(frozen=True)
class FadeOut:
    draw_on_screen: DrawOnScreen
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _elapsed: Millisecond = 0

    def tick(self, time_delta: Millisecond) -> Self:
        if (elapsed := self._elapsed + time_delta) < self.duration:
            remaining = self.duration - elapsed
            alpha = alpha_from_percentage(remaining / self.duration)
            draw_on_screen = self.draw_on_screen.set_alpha(alpha)
            return replace(self, draw_on_screen=draw_on_screen)
        return self
