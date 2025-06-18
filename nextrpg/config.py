"""
Various configurations for `nextrpg`.
You can either use the implicit, default configuration
or pass the customized instance to `nextrpg.start_game.start_game`.
"""

from dataclasses import dataclass, field

from pygame.locals import K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP

from nextrpg.common_types import Direction, Millisecond, Pixel, Rgba, Size


@dataclass(frozen=True)
class DebugConfig:
    """
    Configuration class for debugging purposes.

    This config is used by `nextrpg.draw_on_screen.Drawing`
    for debug visualization and by collision detection systems to
    highlight collision areas.

    Attributes:
        `drawing_background_color`: The background color used for debug drawing.
            Default is semi-transparent blue (0, 0, 255, 32).

        `collision_rectangle_color`: The color used to highlight collision areas
            when debugging is enabled.
            Default is semi-transparent red (255, 0, 0, 96).
    """

    drawing_background_color: Rgba = Rgba(0, 0, 255, 32)
    collision_rectangle_color: Rgba = Rgba(255, 0, 0, 96)


@dataclass(frozen=True)
class GuiConfig:
    """
    Configuration class for Graphical User Interface (GUI).

    This config is used by `nextrpg.start_game.start_game` to initialize
    the pygame window and by the rendering system to control display properties.

    Attributes:
        `title`: The title of the GUI window.

        `size`: The resolution or dimensions of the GUI window defined
            by width and height.

        `frames_per_second`: The target frame rate for the application's
            rendering performance.

        `resize`: Indicates if the GUI window allows resizing by the user.
            And upon resize, the drawings will all be scaled accordingly.

        `background_color`: The background color of the GUI window.
    """

    title: str = "nextrpg"
    size: Size = Size(1280, 800)
    frames_per_second: int = 60
    resize: bool = True
    background_color: Rgba = Rgba(0, 0, 0, 0)


@dataclass(frozen=True)
class TileMapProperties:
    """
    Constants for custom property names used in tile map files.

    This class defines string constants that are used to
    access custom properties defined in TMX map files
    created with Tiled Map Editor.

    This config is used by `nextrpg.scene.map_scene.MapScene`.

    Attributes:
        `speed`: Property name for defining character movement speed.
    """

    speed = "speed"


@dataclass(frozen=True)
class TileMapConfig:
    """
    Configuration class for managing tile map layers and properties,
    that is created from tmx files [Tiled](https://www.mapeditor.org/).

    This config is used by `nextrpg.scene.map_scene.MapScene`.

    Attributes:
        `background`:
            Prefix of layer name to be identified as background layer.

        `foreground`:
            Prefix of layer name to be identified as foreground layer.

        `collision`:
            Prefix of layer name to be identified as collision layer.

        `object`:
            Prefix of layer name to be identified as object layer.

        `player`:
            Name for the player object within object layers.
    """

    background: str = "background"
    foreground: str = "foreground"
    above_character: str = "above_character"
    collision: str = "collision"
    object: str = "object"
    player: str = "player"
    properties: TileMapProperties = TileMapProperties()


@dataclass(frozen=True)
class CharacterConfig:
    """
    Configuration class for characters.

    This config is used by `nextrpg.character.character.Character`.

    Attributes:
        `speed`: The default speed of the character's movement
            in pixels on screen per physical millisecond.
            The number of pixels is consumed before screen scaling, if any.

        `directions`: The set of directions that the character can move.
            Default to all directions (up, left, right, down, and diagonal).
    """

    speed: Pixel = 0.25
    directions: set[Direction] = field(default_factory=lambda: set(Direction))


@dataclass(frozen=True)
class RpgMakerCharacterDrawingConfig:
    """
    Configuration class for RPG Maker character drawings.

    This config is used by
    `nextrpg.character.rpg_maker_drawing.RpgMakerCharacterDrawing`
    to control how character sprites are animated and displayed. It defines the
    animation timing, idle behavior, and default orientation.

    Note that `nextrpg` is only compatible with the RPG Maker character
    sprite sheet format to be able to re-use existing resources.

    However, using RPG Maker's
    [Runtime Time Package (RTP)](https://www.rpgmakerweb.com/run-time-package)
    in non-RPG Maker framework violates the license of RPG Maker,
    even if you own a copy of RPG Maker.

    Attributes:
        `animate_on_idle`: Whether to animate the character when not moving.

        `frame_duration`: The default duration for a single frame for
            the character.

        `direction`: The default initial direction.
    """

    animate_on_idle: bool = False
    frame_duration: Millisecond = 200
    direction: Direction = Direction.DOWN


type KeyCode = int
"""
Type alias for keyboard key codes used in pygame.

This type alias represents integer constants that identify specific keys
on the keyboard (like K_LEFT, K_RIGHT, etc.) as defined by pygame.
These codes are used in key mapping configurations and event handling.
"""


@dataclass(frozen=True)
class KeyMappingConfig:
    """
    Configuration class for keyboard key mappings.

    This class defines the mapping between game actions and keyboard keys.
    Used by `nextrpg.event.pygame_event.KeyboardKey`,
    and the input handling system to translate keyboard input into game actions.

    Attributes:
        `left`: Key code for moving left. The default is `K_LEFT`.

        `right`: Key code for moving right. The default is `K_RIGHT`.

        `up`: Key code for moving up. The default is `K_UP`.

        `down`: Key code for moving down. The default is `K_DOWN`.

        `confirm`: Key code for confirming actions. The default is `K_SPACE`.
    """

    left: KeyCode = K_LEFT
    right: KeyCode = K_RIGHT
    up: KeyCode = K_UP
    down: KeyCode = K_DOWN
    confirm: KeyCode = K_SPACE


@dataclass(frozen=True)
class Config:
    """
    Main configuration class that aggregates all configuration components.

    This is the main configuration object used throughout the application.
    It can be accessed via the `config()` function and
    customized using `set_config()`.

    Attributes:
        `gui`: The configuration for the graphical user interface.
            Used by `nextrpg.start_game.start_game` and rendering systems.

        `map`: The configuration for the tile map structure.
            Used by `nextrpg.scene.map_scene.MapScene` for TMX interpretation.

        `character`: The configuration for character attributes.
            Used by `nextrpg.character.character.Character`
            to control movement properties.

        `rpg_maker_character`: The configuration for RPG Maker
            character drawings. Used by
            `nextrpg.character.rpg_maker_drawing.RpgMakerCharacterDrawing`.

        `key_mapping`: The configuration for keyboard controls.
            Used by `nextrpg.event.pygame_event` for input handling.

        `debug`: The configuration for debugging features.
            Used throughout the codebase when debug rendering is enabled.
            The default is `None` which means debugging is disabled.
            Used by `nextrpg.draw_on_screen.Drawing` for debug visualization
    """

    gui: GuiConfig = GuiConfig()
    map: TileMapConfig = TileMapConfig()
    character: CharacterConfig = CharacterConfig()
    rpg_maker_character: RpgMakerCharacterDrawingConfig = (
        RpgMakerCharacterDrawingConfig()
    )
    key_mapping: KeyMappingConfig = KeyMappingConfig()
    debug: DebugConfig | None = None


_cfg: Config | None = None


def set_config(cfg: Config) -> Config:
    """Sets the global configuration instance.

    Args:
        `cfg`: The `Config` instance to use as the current configuration.

    Returns:
        `Config`: The current `Config` instance after being set.
    """
    global _cfg
    _cfg = cfg
    return _cfg


def config() -> Config:
    """Gets the current configuration instance.

    If no configuration has been set, returns the default `Config` instance.

    Returns:
        `Config`: The current `Config` instance.
    """

    global _cfg
    if _cfg is None:
        _cfg = Config()
    return _cfg
