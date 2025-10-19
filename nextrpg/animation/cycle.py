from dataclasses import KW_ONLY, replace
from typing import Self, override

from nextrpg.animation.sequence import Sequence
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.relative_animation_like import RelativeAnimationLike


@dataclass_with_default(frozen=True)
class Cycle(Sequence):
    _: KW_ONLY = private_init_below()
    _copy: tuple[RelativeAnimationLike, ...] = default(
        lambda self: self.resources
    )

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        if (ticked := super()._tick_before_complete(time_delta)).is_complete:
            return replace(self, resource=self._copy)
        return ticked
