from dataclasses import KW_ONLY, dataclass, field
from typing import ClassVar

from nextrpg.config.config import config
from nextrpg.config.widget.panel_config import PanelConfig
from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.widget.panel import Panel
from nextrpg.widget.sizable_widget_spec import SizableWidgetSpec
from nextrpg.widget.widget_group_spec import WidgetGroupSpec


@dataclass(frozen=True, kw_only=True)
class PanelSpec(WidgetGroupSpec[Panel]):
    name: str
    widgets: tuple[SizableWidgetSpec, ...]
    config: PanelConfig = field(default_factory=lambda: config().widget.panel)
    _: KW_ONLY = private_init_below()
    widget_type: ClassVar[type] = Panel
