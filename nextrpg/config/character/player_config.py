from dataclasses import dataclass

from nextrpg.config.character.behavior_config import BehaviorConfig
from nextrpg.geometry.direction import Direction


@dataclass(frozen=True)
class PlayerConfig(BehaviorConfig):
    directions: frozenset[Direction] = frozenset(Direction)
