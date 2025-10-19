from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.abstract_animation import AbstractAnimation
from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.relative_animation_like import (
    RelativeAnimationLike,
    relative_animation_likes,
)


@dataclass(frozen=True)
class Sequence(AbstractAnimation):
    resource: (
        AnimationLike
        | RelativeAnimationLike
        | tuple[AnimationLike | RelativeAnimationLike, ...]
    )
    _: KW_ONLY = private_init_below()
    _index: int = 0

    @cached_property
    def resources(self) -> tuple[RelativeAnimationLike, ...]:
        return relative_animation_likes(self.resource)

    @override
    @cached_property
    def is_complete(self) -> bool:
        return (
            self._index == len(self.resources) - 1
            and self.resources[-1].is_complete
        )

    @override
    @cached_property
    def drawing(self) -> Drawing | DrawingGroup:
        return self.resources[self._index].resource.drawing

    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        if (ticked := self.resources[self._index].tick(time_delta)).is_complete:
            if (next_index := self._index + 1) < len(self.resources):
                return replace(self, _index=next_index)
        resources = (
            self.resources[: self._index]
            + (ticked,)
            + self.resources[self._index + 1 :]
        )
        return replace(self, resource=resources)
