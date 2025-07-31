from dataclasses import dataclass

from nextrpg.core.direction import Direction
from nextrpg.global_config.character_config import CharacterConfig


@dataclass(frozen=True)
class PlayerConfig(CharacterConfig):
    directions: frozenset[Direction] = frozenset(Direction)
