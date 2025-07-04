"""
Various configurations for `nextrpg`.
You can either use the implicit, default configuration
or pass the customized instance to `nextrpg.start_game.start_game`.
"""

from dataclasses import dataclass
from enum import Enum, IntEnum, auto

from pygame import K_RETURN
from pygame.locals import K_DOWN, K_F1, K_LEFT, K_RIGHT, K_UP

from nextrpg.core import (
    Direction,
    Font,
    Millisecond,
    Pixel,
    PixelPerMillisecond,
    Rgba,
    Size,
)


class LogLevel(IntEnum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


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

        `ignore_map_collisions`: If `True`, the player can move freely on maps,
            ignoring collision areas. Default is `False`.

        `log_level`: The minimum level of log messages to display.

        `log_duration`: The default duration of the log message display
            in milliseconds.
    """

    drawing_background_color: Rgba = Rgba(0, 0, 255, 32)
    collision_rectangle_color: Rgba = Rgba(255, 0, 0, 96)
    ignore_map_collisions: bool = False
    log_level: LogLevel = LogLevel.DEBUG
    log_duration: Millisecond = 3000


class ResizeMode(Enum):
    """
    Resize mode enum.

    Attributes:
        `SCALE`: Scale the images to fit the GUI size.

        `KEEP_NATIVE_SIZE`: Keep the native image size.
    """

    SCALE = auto()
    KEEP_NATIVE_SIZE = auto()


class GuiMode(Enum):
    """
    Gui mode enum.

    Attributes:
        `WINDOWED`: Windowed GUI.

        `FULL_SCREEN`: Full screen GUI.
    """

    WINDOWED = auto()
    FULL_SCREEN = auto()

    @property
    def opposite(self) -> GuiMode:
        """
        Get the opposite gui mode.

        Returns:
            `GuiMode`: The opposite gui mode.
        """
        return _OPPOSITE_GUI_MODE[self]


_OPPOSITE_GUI_MODE = {
    GuiMode.WINDOWED: GuiMode.FULL_SCREEN,
    GuiMode.FULL_SCREEN: GuiMode.WINDOWED,
}


@dataclass(frozen=True)
class GuiConfig:
    """
    Configuration class for Graphical User Interface (GUI).

    This is used by `nextrpg.gui.Gui` to initialize
    the pygame window and by the rendering system to control display properties.

    Attributes:
        `title`: The title of the GUI window.

        `size`: The resolution or dimensions of the GUI window defined
            by width and height. This also defines the aspect ratio of the game.

        `frames_per_second`: The target frame rate for the application's
            rendering performance.

        `background_color`: The background color of the GUI window.

        `gui_mode`: Whether to start the game in windowed or full screen mode.

        `resize_mode`: Whether to scale the images to fit the GUI size,
            or keep the native image size.

        `allow_window_resize`: Whether to allow the user to resize the window
            in windowed mode.
    """

    title: str = "nextrpg"
    size: Size = Size(1280, 720)
    frames_per_second: int = 60
    background_color: Rgba = Rgba(0, 0, 0, 0)
    gui_mode: GuiMode = GuiMode.WINDOWED
    resize_mode: ResizeMode = ResizeMode.SCALE
    allow_window_resize: bool = True


@dataclass(frozen=True)
class TileMapConfig:
    """
    Configuration class for managing tile map layers and properties,
    that is created from tmx files [Tiled](https://www.mapeditor.org/).

    This config is used by `nextrpg.scene.map_scene.MapScene`.

    Attributes:
        `background`:
            Class name of the layer to be identified as background layer.

        `foreground`:
            Class name of the layer to be identified as foreground layer.

        `collision`:
            Class name of the objects to be identified as collision objects.
    """

    background: str = "background"
    foreground: str = "foreground"
    above_character: str = "above_charactet"
    collision: str = "collision"


@dataclass(frozen=True)
class CharacterConfig:
    """
    Configuration class for characters.

    This config is used by `nextrpg.character.character.Character`.

    Attributes:
        `move_speed`: The default speed of the character's movement
            in pixels on screen per physical millisecond.
            The number of pixels is consumed before screen scaling, if any.

        `idle_duration`: The duration of the NPC's idle duration.

        `move_duration`: The duration of the NPC's move duration.

        `directions`: The set of directions that the player can move.
            Default to all directions (up, left, right, down, and diagonals).
    """

    move_speed: PixelPerMillisecond = 0.25
    idle_duration: Millisecond = 1000
    move_duration: Millisecond = 2000
    directions: frozenset[Direction] = frozenset(Direction)


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
        `frame_duration`: The default duration for a single frame for
            the character.
    """

    duration_per_frame: Millisecond = 150


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

        `gui_mode_toggle`: Key code for toggling between
            windowed and full screen mode. The default is `F1`.
    """

    left: KeyCode = K_LEFT
    right: KeyCode = K_RIGHT
    up: KeyCode = K_UP
    down: KeyCode = K_DOWN
    confirm: KeyCode = K_RETURN
    gui_mode_toggle: KeyCode | None = K_F1


@dataclass(frozen=True)
class ResourceConfig:
    """
    Configuration class for resource loading.

    Attributes:
        `map_cache_size`: The maximum number of TMX maps to cache in memory.
    """

    map_cache_size: int = 8
    drawing_cache_size: int = 8


@dataclass(frozen=True)
class TransitionConfig:
    """
    Configuration class for transition scenes.

    This config is used by `nextrpg.scene.transition_scene.TransitionScene`.

    Arguments:
        `transition_duration`: The total duration of the transition
            in milliseconds.
    """

    transition_duration: Millisecond = 500


@dataclass(frozen=True)
class TextConfig:
    """
    Configuration class for text rendering.

    Arguments:
        `font`: The font to use for rendering text.

        `color`: The color to use for rendering text.

        `margin`: The margin to use for rendering text.

        `antialias`: Whether to use antialiasing for rendering text.
    """

    font: Font = Font(24)
    color: Rgba = Rgba(255, 255, 255, 255)
    margin: Pixel = 4
    antialias: bool = True


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

        `resource`: The configuration for resource loading.

        `transition`: The configuration for transition scenes.

        `text`: The configuration for text rendering.

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
    resource: ResourceConfig = ResourceConfig()
    transition: TransitionConfig = TransitionConfig()
    text: TextConfig = TextConfig()
    debug: DebugConfig | None = None


def set_config(cfg: Config):
    """Sets the global configuration instance.

    Arguments:
        `cfg`: The `Config` instance to use as the current configuration.

    Returns:
        `None`
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
        `Config`: The current `Config` instance.
    """
    global _cfg
    if not _cfg:
        set_config(Config())
    return _cfg


def initial_config() -> Config:
    """
    Get the initial configuration instance. This is useful for getting
    the native/initial GUI resolution.

    Returns:
        `Config`: The initial `Config` before any GUI/configuration changes.
    """
    if not _initial_config:
        set_config(Config())
    return _initial_config


_initial_config: Config | None = None
_cfg: Config | None = None
