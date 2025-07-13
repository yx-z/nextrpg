from functools import cached_property
from typing import override

from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.draw.fade import Fade
from nextrpg.model import dataclass_with_instance_init, instance_init


@dataclass_with_instance_init
class FadeOut(Fade):
    _start: tuple[DrawOnScreen, ...] = instance_init(lambda self: self.resource)

    @override
    @cached_property
    def _percentage(self) -> float:
        remaining = self.duration - self._elapsed
        return remaining / self.duration

    @override
    @cached_property
    def _complete(self) -> tuple[DrawOnScreen, ...]:
        return ()
