from typing import Any, Self

from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.geometry.direction import Direction


class CharacterDrawing(AnimationLike):
    direction: Direction = Direction.UP

    def turn(self, direction: Direction) -> Self:
        return self

    def tick_idle(self, time_delta: Millisecond) -> Self:
        return self

    def tick_action(self, time_delta: Millisecond, action: Any) -> Self:
        return self
