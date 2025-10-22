from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

from nextrpg.config.character.character_config import CharacterConfig
from nextrpg.config.character.player_config import PlayerConfig
from nextrpg.config.character.rpg_maker_character_drawing_config import (
    RpgMakerCharacterDrawingConfig,
)
from nextrpg.config.drawing.drawing_config import DrawingConfig
from nextrpg.config.drawing.text_config import TextConfig
from nextrpg.config.drawing.text_group_config import TextGroupConfig
from nextrpg.config.map_config import MapConfig
from nextrpg.config.menu_config import MenuConfig
from nextrpg.config.rpg_event.cutscene_config import CutsceneConfig
from nextrpg.config.rpg_event.rpg_event_config import RpgEventConfig
from nextrpg.config.rpg_event.say_event_config import SayEventConfig
from nextrpg.config.save_config import SaveConfig
from nextrpg.config.system.debug_config import DebugConfig
from nextrpg.config.system.game_loop_config import GameLoopConfig
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.config.system.window_config import WindowConfig
from nextrpg.config.timing_config import TimingConfig
from nextrpg.config.widget.widget_config import WidgetConfig


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
    timing: TimingConfig = TimingConfig()
    text: TextConfig = TextConfig()
    text_group: TextGroupConfig = TextGroupConfig()
    drawing: DrawingConfig = DrawingConfig()
    event: RpgEventConfig = RpgEventConfig()
    say_event: SayEventConfig = SayEventConfig()
    cutscene: CutsceneConfig = CutsceneConfig()
    save: SaveConfig = SaveConfig()
    game_loop: GameLoopConfig = GameLoopConfig()
    widget: WidgetConfig = WidgetConfig()
    menu: MenuConfig = MenuConfig()


def set_config(cfg: Config) -> Config:
    global _initial_config
    global _cfg
    if not _initial_config:
        _initial_config = cfg
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
