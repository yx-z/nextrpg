from dataclasses import dataclass, field

from nextrpg.config.drawing.text_config import TextConfig
from nextrpg.config.logging_config import LoggingConfig
from nextrpg.drawing.color import BLUE, GREEN, RED, Color
from nextrpg.geometry.size import Height


def _widget_metadata_text() -> TextConfig:
    from nextrpg.config.config import config

    return config().drawing.text.with_font_size(Height(12))


@dataclass(frozen=True)
class DebugConfig:
    player_collide_with_others: bool = True
    drawing_background: Color | None = Color(0, 0, 255, 8)
    collision_rectangle: Color | None = Color(255, 0, 0, 64)
    start_event_rectangle: Color | None = Color(0, 255, 255, 32)
    move_object: Color | None = Color(255, 255, 0, 200)
    npc_path: Color | None = Color(0, 255, 0, 64)
    drawing_group_link: Color | None = RED
    widget_link_color: Color | None = GREEN
    widget_group_border: Color | None = BLUE
    widget_metadata_text: TextConfig | None = field(
        default_factory=_widget_metadata_text
    )
    logging: LoggingConfig | None = LoggingConfig()
