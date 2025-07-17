"""
Various configurations for `nextrpg`.

You can either use the implicit, default configuration or pass the customized
instance to `nextrpg.start_game.start_game`.
"""

from dataclasses import dataclass

from nextrpg.global_config.character_config import CharacterConfig
from nextrpg.global_config.debug_config import DebugConfig
from nextrpg.global_config.draw_on_screen_config import DrawOnScreenConfig
from nextrpg.global_config.event_config import EventConfig
from nextrpg.global_config.gui_config import GuiConfig
from nextrpg.global_config.key_mapping_config import KeyMappingConfig
from nextrpg.global_config.resource_config import ResourceConfig
from nextrpg.global_config.rpg_maker_character_drawing_config import (
    RpgMakerCharacterDrawingConfig,
)
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.global_config.text_config import TextConfig
from nextrpg.global_config.tile_map_config import TileMapConfig
from nextrpg.global_config.transition_config import TransitionConfig


@dataclass(frozen=True)
class Config:
    """
    Main configuration class that aggregates all configuration components.

    This is the main configuration object used throughout the application. It
    can be accessed via the `global_config()` function and customized using
    `set_config()`.

    Attributes:
        gui: The configuration for the graphical user interface. Used by
            `nextrpg.start_game.start_game` and rendering systems.
        map: The configuration for the tile map structure. Used by
            `nextrpg.scene.map_scene.MapScene` for TMX interpretation.
        character: The configuration for character attributes. Used by
            `nextrpg.character.character.Character` to control movement
            properties.
        rpg_maker_character: The configuration for RPG Maker character drawings.
            Used by `nextrpg.character.rpg_maker_drawing.RpgMakerCharacterDrawing`.
        key_mapping: The configuration for keyboard controls. Used by
            `nextrpg.event.pygame_event` for input handling.
        resource: The configuration for resource loading.
        transition: The configuration for transition scenes.
        text: The configuration for text rendering.
        debug: The configuration for debugging features. Used throughout the
            codebase when debug rendering is enabled. The default is `None`
            which means debugging is disabled. Used by
            `nextrpg.draw_on_screen.Drawing` for debug visualization.
    """

    gui: GuiConfig = GuiConfig()
    map: TileMapConfig = TileMapConfig()
    character: CharacterConfig = CharacterConfig()
    rpg_maker_character: RpgMakerCharacterDrawingConfig = (
        RpgMakerCharacterDrawingConfig()
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
    """Sets the global configuration instance.

    Arguments:
        cfg: The `Config` instance to use as the current configuration.

    Returns:
        None
    """
    global _initial_config
    global _cfg
    if not _initial_config:
        _initial_config = cfg
    _cfg = cfg


def config() -> Config:
    """Gets the current configuration instance.

    If no configuration has been set, returns the default `Config` instance.

    Returns:
        The current `Config` instance.
    """
    global _cfg
    if not _cfg:
        set_config(Config())
    return _cfg


def initial_config() -> Config:
    """
    Get the initial configuration instance. This is useful for getting the
    native/initial GUI resolution.

    Returns:
        The initial `Config` before any GUI/configuration changes.
    """
    if not _initial_config:
        set_config(Config())
    return _initial_config


_initial_config: Config | None = None
_cfg: Config | None = None
