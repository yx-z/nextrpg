from dataclasses import dataclass

from nextrpg.core.dimension import PixelPerMillisecond
from nextrpg.core.direction import Direction
from nextrpg.core.time import Millisecond


@dataclass(frozen=True)
class CharacterConfig:
    move_speed: PixelPerMillisecond = 0.2
    idle_duration: Millisecond = 500
    move_duration: Millisecond = 1000
    directions: frozenset[Direction] = frozenset(Direction)
