"""
Debug configuration system for `nextrpg`.

This module provides configuration options for debugging features in `nextrpg`
games. It includes log levels, debug visualization settings, and collision
detection debugging options.

Features:
    - Log level enumeration for message filtering
    - Debug visualization colors for drawing and collision areas
    - Collision detection debugging options
    - Configurable log message duration
    - NPC path visualization settings
"""

from dataclasses import dataclass
from enum import IntEnum, auto

from nextrpg.core.time import Millisecond
from nextrpg.draw.color import Rgba


class LogLevel(IntEnum):
    """
    Enumeration of log levels for message filtering.

    This enum defines the different levels of log messages, from most detailed
    (DEBUG) to most critical (ERROR). Log levels are used to filter which
    messages are displayed based on the current debug configuration.

    Attributes:
        DEBUG: Most detailed level for development and debugging.
        INFO: General information about game events.
        WARNING: Important information that may indicate issues.
        ERROR: Critical errors that need immediate attention.
    """

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass(frozen=True)
class DebugConfig:
    """
    Configuration class for debugging purposes.

    This global_config is used by `nextrpg.draw_on_screen.Drawing` for debug
    visualization and by collision detection systems to highlight collision
    areas.

    Arguments:
        draw_background_color: The background color used for debug drawing.
            Default is semi-transparent blue (0, 0, 255, 16).
        collision_rectangle_color: The color used to highlight collision areas
            when debugging is enabled. Default is semi-transparent red (255, 0,
            0, 64).
        npc_path_color: The color used to visualize NPC movement paths. Default
            is semi-transparent green (0, 255, 0, 64).
        ignore_map_collisions: If True, the player can move freely on maps,
            ignoring collision areas. Default is False.
        log_level: The minimum level of log messages to display.
        log_duration: The default duration of log messages in milliseconds.
    """

    draw_background_color: Rgba | None = Rgba(0, 0, 255, 16)
    collision_rectangle_color: Rgba | None = Rgba(255, 0, 0, 64)
    npc_path_color: Rgba | None = Rgba(0, 255, 0, 64)
    ignore_map_collisions: bool = False
    log_level: LogLevel = LogLevel.DEBUG
    log_duration: Millisecond = 3000
