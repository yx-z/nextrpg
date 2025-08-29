from dataclasses import dataclass

from nextrpg.config.character_config import CharacterConfig
from nextrpg.geometry.direction import Direction


@dataclass(frozen=True)
class PlayerConfig(CharacterConfig):
    directions: frozenset[Direction] = frozenset(Direction)
