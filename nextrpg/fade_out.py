from functools import cached_property
from typing import override

from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.fade import Fade
from nextrpg.model import (
    dataclass_with_instance_init,
    instance_init,
    export,
)


@export
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
