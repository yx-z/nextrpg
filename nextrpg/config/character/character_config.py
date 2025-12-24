from dataclasses import dataclass

from nextrpg.config.character.behavior_config import BehaviorConfig
from nextrpg.config.character.player_config import PlayerConfig
from nextrpg.config.character.rpg_maker_character_drawing_config import (
    RpgMakerCharacterDrawingConfig,
)


@dataclass(frozen=True)
class CharacterConfig:
    behavior: BehaviorConfig = BehaviorConfig()
    player: PlayerConfig = PlayerConfig()
    rpg_maker_character_drawing: RpgMakerCharacterDrawingConfig = (
        RpgMakerCharacterDrawingConfig()
    )
