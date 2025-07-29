from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

from nextrpg.global_config.character_config import CharacterConfig
from nextrpg.global_config.debug_config import DebugConfig
from nextrpg.global_config.draw_on_screen_config import DrawOnScreenConfig
from nextrpg.global_config.event_config import EventConfig
from nextrpg.global_config.gui_config import GuiConfig
from nextrpg.global_config.key_mapping_config import KeyMappingConfig
from nextrpg.global_config.resource_config import ResourceConfig
from nextrpg.global_config.rpg_maker_character_draw_config import (
    RpgMakerCharacterDrawConfig,
)
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.global_config.text_config import TextConfig
from nextrpg.global_config.tile_map_config import TileMapConfig
from nextrpg.global_config.transition_config import TransitionConfig


@dataclass(frozen=True)
class Config:
    gui: GuiConfig = GuiConfig()
    map: TileMapConfig = TileMapConfig()
    character: CharacterConfig = CharacterConfig()
    rpg_maker_character: RpgMakerCharacterDrawConfig = (
        RpgMakerCharacterDrawConfig()
    )
    key_mapping: KeyMappingConfig = KeyMappingConfig()
    resource: ResourceConfig = ResourceConfig()
    transition: TransitionConfig = TransitionConfig()
    text: TextConfig = TextConfig()
    draw_on_screen: DrawOnScreenConfig = DrawOnScreenConfig()
    event: EventConfig = EventConfig()
    say_event: SayEventConfig = SayEventConfig()
    debug: DebugConfig | None = None


def set_config(cfg: Config):
    global _initial_config
    global _cfg
    if not _initial_config:
        _initial_config = cfg
    _cfg = cfg


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
