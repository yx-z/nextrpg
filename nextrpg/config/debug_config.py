from dataclasses import dataclass
from enum import IntEnum, auto

from nextrpg.core import Millisecond, Rgba


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

        `log_duration`: The default duration of the log message is displayed
            in milliseconds.
    """

    drawing_background_color: Rgba | None = Rgba(0, 0, 255, 16)
    collision_rectangle_color: Rgba | None = Rgba(255, 0, 0, 64)
    npc_path_color: Rgba | None = Rgba(0, 255, 0, 64)
    ignore_map_collisions: bool = False
    log_level: LogLevel = LogLevel.DEBUG
    log_duration: Millisecond = 3000
