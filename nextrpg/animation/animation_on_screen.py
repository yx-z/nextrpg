from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.base_animation_on_screen import (
    BaseAnimationOnScreen,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.sprite import Sprite
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class AnimationOnScreen(BaseAnimationOnScreen):
    coordinate: Coordinate
    resource: Sprite
    anchor: Anchor = Anchor.TOP_LEFT

    @override
    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        return self.resource.drawing_on_screens(self.coordinate)

    @override
    @cached_property
    def is_complete(self) -> bool:
        return self.resource.is_complete

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        resource = self.resource.tick(time_delta)
        return replace(self, resource=resource)
