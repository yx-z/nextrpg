from dataclasses import dataclass

from nextrpg.config.widget.panel_config import PanelConfig


@dataclass(frozen=True)
class WidgetConfig:
    panel: PanelConfig = PanelConfig()
