from dataclasses import dataclass
from enum import IntEnum, auto

from nextrpg.core.color import Color
from nextrpg.core.time import Millisecond


class LogLevel(IntEnum):
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass(frozen=True, slots=True)
class DebugConfig:
    drawing_background_color: Color | None = Color(0, 0, 255, 16)
    collision_rectangle_color: Color | None = Color(255, 0, 0, 64)
    start_event_rectangle_color: Color | None = Color(0, 255, 255, 64)
    move_object_color: Color | None = Color(255, 255, 0, 180)
    npc_path_color: Color | None = Color(0, 255, 0, 64)
    draw_group_link_color: Color | None = Color(255, 0, 255, 64)
    player_collide_with_others: bool = True
    log_level: LogLevel = LogLevel.DEBUG
    log_duration: Millisecond = 3000


def log_only(log_level: LogLevel = LogLevel.DEBUG) -> DebugConfig:
    return DebugConfig(
        drawing_background_color=None,
        collision_rectangle_color=None,
        start_event_rectangle_color=None,
        move_object_color=None,
        npc_path_color=None,
        draw_group_link_color=None,
        player_collide_with_others=False,
        log_level=log_level,
    )
