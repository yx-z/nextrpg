from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

from nextrpg.global_config.character_config import CharacterConfig
from nextrpg.global_config.cutscene_config import CutsceneConfig
from nextrpg.global_config.debug_config import DebugConfig
from nextrpg.global_config.drawing_config import DrawingConfig
from nextrpg.global_config.event_config import EventConfig
from nextrpg.global_config.game_loop_config import GameLoopConfig
from nextrpg.global_config.key_mapping_config import KeyMappingConfig
from nextrpg.global_config.map_config import MapConfig
from nextrpg.global_config.player_config import PlayerConfig
from nextrpg.global_config.rpg_maker_character_drawing_config import (
    RpgMakerCharacterDrawingConfig,
)
from nextrpg.global_config.save_config import SaveConfig
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.global_config.text_config import TextConfig
from nextrpg.global_config.text_group_config import TextGroupConfig
from nextrpg.global_config.transition_config import TransitionConfig
from nextrpg.global_config.window_config import WindowConfig


@dataclass(frozen=True)
class Config:
    debug: DebugConfig | None = None
    window: WindowConfig = WindowConfig()
    map: MapConfig = MapConfig()
    character: CharacterConfig = CharacterConfig()
    player: PlayerConfig = PlayerConfig()
    rpg_maker_character: RpgMakerCharacterDrawingConfig = (
        RpgMakerCharacterDrawingConfig()
    )
    key_mapping: KeyMappingConfig = KeyMappingConfig()
    transition: TransitionConfig = TransitionConfig()
    text: TextConfig = TextConfig()
    text_group: TextGroupConfig = TextGroupConfig()
    drawing: DrawingConfig = DrawingConfig()
    event: EventConfig = EventConfig()
    say_event: SayEventConfig = SayEventConfig()
    cutscene: CutsceneConfig = CutsceneConfig()
    save: SaveConfig = SaveConfig()
    game_loop: GameLoopConfig = GameLoopConfig()


def set_config(cfg: Config) -> Config:
    global _initial_config
    global _cfg
    if not _initial_config:
        _initial_config = cfg

    if _cfg and cfg.window != _cfg.window:
        from nextrpg.core.save import SaveIo

        SaveIo().save(cfg.window)

    _cfg = cfg
    return _cfg


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


_initial_config: Config | None = None
_cfg: Config | None = None
