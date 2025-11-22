from dataclasses import dataclass

from nextrpg.config.drawing.text_config import TextConfig
from nextrpg.config.drawing.text_group_config import TextGroupConfig


@dataclass(frozen=True)
class DrawingConfig:
    text: TextConfig = TextConfig()
    text_group: TextGroupConfig = TextGroupConfig()
