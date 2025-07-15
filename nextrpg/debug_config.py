"""
Debug configuration system for NextRPG.

This module provides configuration options for debugging features
in NextRPG games. It includes log levels, debug visualization
settings, and collision detection debugging options.

The debug system features:
- Log level enumeration for message filtering
- Debug visualization colors for drawing and collision areas
- Collision detection debugging options
- Configurable log message duration
- NPC path visualization settings

Example:
    ```python
    from nextrpg.debug_config import DebugConfig, LogLevel
    from nextrpg.core import Rgba

    # Create debug config
    debug_config = DebugConfig(
        log_level=LogLevel.INFO,
        log_duration=5000,
        ignore_map_collisions=True
    )
    ```
"""

from dataclasses import dataclass
from enum import IntEnum, auto

from nextrpg.core import Millisecond, Rgba
from nextrpg.model import export


@export
class LogLevel(IntEnum):
    """
    Enumeration of log levels for message filtering.

    This enum defines the different levels of log messages,
    from most detailed (DEBUG) to most critical (ERROR).
    Log levels are used to filter which messages are displayed
    based on the current debug configuration.

    Attributes:
        `DEBUG`: Most detailed level for development and debugging.
        `INFO`: General information about game events.
        `WARNING`: Important information that may indicate issues.
        `ERROR`: Critical errors that need immediate attention.

    Example:
        ```python
        from nextrpg.debug_config import LogLevel

        # Check log level
        if current_level >= LogLevel.INFO:
            # Display info messages
            pass
        ```
    """

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@export
@dataclass(frozen=True)
class DebugConfig:
    """
    Configuration class for debugging purposes.

    This config is used by `nextrpg.draw_on_screen.Drawing`
    for debug visualization and by collision detection systems to
    highlight collision areas.

    Arguments:
        `drawing_background_color`: The background color used for debug drawing.
            Default is semi-transparent blue (0, 0, 255, 16).

        `collision_rectangle_color`: The color used to highlight collision areas
            when debugging is enabled.
            Default is semi-transparent red (255, 0, 0, 64).

        `npc_path_color`: The color used to visualize NPC movement paths.
            Default is semi-transparent green (0, 255, 0, 64).

        `ignore_map_collisions`: If `True`, the player can move freely on maps,
            ignoring collision areas. Default is `False`.

        `log_level`: The minimum level of log messages to display.

        `log_duration`: The default duration of log messages in milliseconds.

    Example:
        ```python
        from nextrpg.debug_config import DebugConfig, LogLevel
        from nextrpg.core import Rgba

        # Create debug config for development
        debug_config = DebugConfig(
            drawing_background_color=Rgba(255, 255, 0, 32),  # Yellow
            collision_rectangle_color=Rgba(255, 0, 255, 64),  # Magenta
            ignore_map_collisions=True,
            log_level=LogLevel.DEBUG,
            log_duration=5000
        )
        ```
    """

    drawing_background_color: Rgba | None = Rgba(0, 0, 255, 16)
    collision_rectangle_color: Rgba | None = Rgba(255, 0, 0, 64)
    npc_path_color: Rgba | None = Rgba(0, 255, 0, 64)
    ignore_map_collisions: bool = False
    log_level: LogLevel = LogLevel.DEBUG
    log_duration: Millisecond = 3000
