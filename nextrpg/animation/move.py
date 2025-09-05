from dataclasses import dataclass

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.geometry.direction import Direction, DirectionalOffset


@dataclass(frozen=True)
class Move(AnimationOnScreens):
    offset: DirectionalOffset
