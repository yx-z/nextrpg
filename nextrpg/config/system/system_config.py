from dataclasses import dataclass

from nextrpg.config.system.debug_config import DebugConfig
from nextrpg.config.system.game_loop_config import GameLoopConfig
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.config.system.resource_config import ResourceConfig
from nextrpg.config.system.save_config import SaveConfig
from nextrpg.config.system.sound_config import SoundConfig
from nextrpg.config.system.window_config import WindowConfig


@dataclass(frozen=True)
class SystemConfig:
    window: WindowConfig = WindowConfig()
    resource: ResourceConfig = ResourceConfig()
    sound: SoundConfig = SoundConfig()
    save: SaveConfig = SaveConfig()
    key_mapping: KeyMappingConfig = KeyMappingConfig()
    game_loop: GameLoopConfig = GameLoopConfig()
    debug: DebugConfig | None = None
