from contextlib import contextmanager
from dataclasses import dataclass, replace
from typing import Generator

from nextrpg.config.character.character_config import CharacterConfig
from nextrpg.config.character.player_config import PlayerConfig
from nextrpg.config.character.rpg_maker_character_drawing_config import (
    RpgMakerCharacterDrawingConfig,
)
from nextrpg.config.drawing.animation_config import AnimationConfig
from nextrpg.config.drawing.text_config import TextConfig
from nextrpg.config.drawing.text_group_config import TextGroupConfig
from nextrpg.config.item_config import ItemConfig
from nextrpg.config.map_config import MapConfig
from nextrpg.config.menu_config import MenuConfig
from nextrpg.config.rpg_event.cutscene_config import CutsceneConfig
from nextrpg.config.rpg_event.rpg_event_config import RpgEventConfig
from nextrpg.config.rpg_event.say_event_config import SayEventConfig
from nextrpg.config.system.debug_config import DebugConfig
from nextrpg.config.system.game_loop_config import GameLoopConfig
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.config.system.resource_config import ResourceConfig
from nextrpg.config.system.save_config import SaveConfig
from nextrpg.config.system.sound_config import SoundConfig
from nextrpg.config.system.window_config import WindowConfig
from nextrpg.config.widget.widget_config import WidgetConfig


@dataclass(frozen=True)
class Config:
    window: WindowConfig = WindowConfig()
    map: MapConfig = MapConfig()
    character: CharacterConfig = CharacterConfig()
    player: PlayerConfig = PlayerConfig()
    rpg_maker_character: RpgMakerCharacterDrawingConfig = (
        RpgMakerCharacterDrawingConfig()
    )
    sound: SoundConfig = SoundConfig()
    key_mapping: KeyMappingConfig = KeyMappingConfig()
    animation: AnimationConfig = AnimationConfig()
    text: TextConfig = TextConfig()
    text_group: TextGroupConfig = TextGroupConfig()
    event: RpgEventConfig = RpgEventConfig()
    say_event: SayEventConfig = SayEventConfig()
    cutscene: CutsceneConfig = CutsceneConfig()
    save: SaveConfig = SaveConfig()
    game_loop: GameLoopConfig = GameLoopConfig()
    widget: WidgetConfig = WidgetConfig()
    resource: ResourceConfig = ResourceConfig()
    item: ItemConfig = ItemConfig()
    menu: MenuConfig | None = None
    debug: DebugConfig | None = None


_initial_config: Config | None = None
_cfg: Config | None = None
_last_debug_config: DebugConfig | None = None


def set_config(cfg: Config) -> Config:
    global _initial_config
    global _cfg
    global _last_debug_config
    if not _initial_config:
        _initial_config = cfg
    if cfg.debug:
        _last_debug_config = cfg.debug
    _cfg = cfg
    return _cfg


def force_debug_config() -> DebugConfig:
    global _last_debug_config
    if _last_debug_config:
        return _last_debug_config
    cfg = config()
    debug = DebugConfig()
    cfg = replace(cfg, debug=debug)
    set_config(cfg)
    return debug


def config() -> Config:
    global _cfg
    if not _cfg:
        set_config(Config())
    return _cfg


def initial_config() -> Config:
    if not _initial_config:
        set_config(Config())
    return _initial_config


@contextmanager
def override_config(cfg: Config) -> Generator[Config, None, None]:
    prev = config()
    try:
        yield set_config(cfg)
    finally:
        set_config(prev)
