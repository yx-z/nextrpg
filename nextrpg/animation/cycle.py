from dataclasses import KW_ONLY
from typing import override

from nextrpg.animation.sequence import Sequence
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.shifted_sprite import ShiftedSprite
from nextrpg.drawing.sprite import Sprite


@dataclass_with_default(frozen=True)
class Cycle(Sequence):
    _: KW_ONLY = private_init_below()
    _copy: tuple[ShiftedSprite, ...] = default(lambda self: self.resources)

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Sprite:
        if (ticked := super()._tick_before_complete(time_delta)).is_complete:
            return Cycle(self._copy)
        return ticked
