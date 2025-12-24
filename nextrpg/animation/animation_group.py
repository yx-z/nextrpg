from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.base_animation import (
    BaseAnimation,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.shifted_sprite import (
    ShiftedSprite,
    shifted_sprites,
)
from nextrpg.drawing.sprite import Sprite, tick_all


@dataclass(frozen=True)
class AnimationGroup(BaseAnimation):
    resource: Sprite | ShiftedSprite | tuple[Sprite | ShiftedSprite, ...]

    def concur(self, another: ShiftedSprite) -> Self:
        resource = self.resources + (another,)
        return replace(self, resource=resource)

    @cached_property
    def resources(self) -> tuple[ShiftedSprite, ...]:
        return shifted_sprites(self.resource)

    @override
    @cached_property
    def is_complete(self) -> bool:
        return all(
            relative_drawing.is_complete for relative_drawing in self.resources
        )

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        return DrawingGroup(self.resources)

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        resource = tick_all(self.resources, time_delta)
        return replace(self, resource=resource)
