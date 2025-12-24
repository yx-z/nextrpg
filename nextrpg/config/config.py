from contextlib import contextmanager
from dataclasses import dataclass, replace
from typing import Generator

from nextrpg.config.animation_config import AnimationConfig
from nextrpg.config.character.character_config import CharacterConfig
from nextrpg.config.debug_config import DebugConfig
from nextrpg.config.drawing.drawing_config import DrawingConfig
from nextrpg.config.event.event_config import RpgEventConfig
from nextrpg.config.map_config import MapConfig
from nextrpg.config.menu_config import MenuConfig
from nextrpg.config.rpg.rpg_config import RpgConfig
from nextrpg.config.system.system_config import SystemConfig
from nextrpg.config.widget.widget_config import WidgetConfig


@dataclass(frozen=True)
class Config:
    map: MapConfig = MapConfig()
    character: CharacterConfig = CharacterConfig()
    animation: AnimationConfig = AnimationConfig()
    event: RpgEventConfig = RpgEventConfig()
    widget: WidgetConfig = WidgetConfig()
    rpg: RpgConfig = RpgConfig()
    system: SystemConfig = SystemConfig()
    drawing: DrawingConfig = DrawingConfig()
    menu: MenuConfig | None = None
    debug: DebugConfig | None = None


_initial_config: Config | None = None
_config: Config | None = None
_latest_debug_config: DebugConfig | None = None


def set_config(cfg: Config) -> Config:
    global _initial_config
    global _config
    global _latest_debug_config
    if not _initial_config:
        _initial_config = cfg
    if cfg.debug:
        _latest_debug_config = cfg.debug
    _config = cfg
    return cfg


def force_debug_config() -> DebugConfig:
    if _latest_debug_config:
        return _latest_debug_config
    debug = DebugConfig()
    current_config = config()
    cfg = replace(current_config, debug=debug)
    set_config(cfg)
    return debug


def config() -> Config:
    if _config:
        return _config
    cfg = Config()
    return set_config(cfg)


def initial_config() -> Config:
    if _initial_config:
        return _initial_config
    cfg = Config()
    return set_config(cfg)


@contextmanager
def override_config(cfg: Config) -> Generator[Config, None, None]:
    prev = config()
    try:
        yield set_config(cfg)
    finally:
        set_config(prev)
