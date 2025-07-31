from dataclasses import dataclass
from enum import IntEnum, auto

from nextrpg.core.color import Color
from nextrpg.core.time import Millisecond


class LogLevel(IntEnum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass(frozen=True)
class DebugConfig:
    draw_background_color: Color | None = Color(0, 0, 255, 16)
    collision_rectangle_color: Color | None = Color(255, 0, 0, 64)
    npc_path_color: Color | None = Color(0, 255, 0, 64)
    ignore_map_collisions: bool = False
    log_level: LogLevel = LogLevel.DEBUG
    log_duration: Millisecond = 3000
