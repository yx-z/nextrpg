from dataclasses import dataclass

from nextrpg.config.widget.button_config import ButtonConfig
from nextrpg.config.widget.panel_config import PanelConfig


@dataclass(frozen=True)
class WidgetConfig:
    button: ButtonConfig = ButtonConfig()
    panel: PanelConfig = PanelConfig()
