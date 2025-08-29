from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

from nextrpg.config.character_config import CharacterConfig
from nextrpg.config.cutscene_config import CutsceneConfig
from nextrpg.config.debug_config import DebugConfig
from nextrpg.config.drawing_config import DrawingConfig
from nextrpg.config.event_config import EventConfig
from nextrpg.config.game_loop_config import GameLoopConfig
from nextrpg.config.key_mapping_config import KeyMappingConfig
from nextrpg.config.map_config import MapConfig
from nextrpg.config.player_config import PlayerConfig
from nextrpg.config.rpg_maker_character_drawing_config import (
    RpgMakerCharacterDrawingConfig,
)
from nextrpg.config.save_config import SaveConfig
from nextrpg.config.say_event_config import SayEventConfig
from nextrpg.config.text_config import TextConfig
from nextrpg.config.text_group_config import TextGroupConfig
from nextrpg.config.transition_config import TransitionConfig
from nextrpg.config.window_config import WindowConfig


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
