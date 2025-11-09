from dataclasses import dataclass

from nextrpg.config.widget.button_config import ButtonConfig


@dataclass(frozen=True)
class WidgetConfig:
    button: ButtonConfig = ButtonConfig()
