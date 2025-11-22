from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import Any, ClassVar

from nextrpg.config.widget.panel_config import PanelConfig
from nextrpg.core.dataclass_with_default import (
    private_init_below,
)
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.widget.sizable_widget import SizableWidget
from nextrpg.widget.widget import Widget
from nextrpg.widget.widget_group import WidgetGroup, WidgetGroupOnScreen


@dataclass(frozen=True, kw_only=True)
class PanelOnScreen(WidgetGroupOnScreen):
    widget: Panel

    @cached_property
    def area(self) -> AreaOnScreen:
        assert isinstance(
            self.on_screen, AreaOnScreen
        ), f"Expect AreaOnScreen for {self.widget.name}. Got {self.on_screen}."
        return self.on_screen


@dataclass(frozen=True, kw_only=True)
class Panel(WidgetGroup[PanelOnScreen]):
    name: str
    children: tuple[Widget, ...] | Callable[[PanelOnScreen], tuple[Widget, ...]]
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = PanelOnScreen


def panel_vbox[_SizableWidget: SizableWidget](
    widget_type: type[_SizableWidget],
    specs: tuple[Any, ...],
    config: PanelConfig | None = None,
) -> Callable[[PanelOnScreen], tuple[_SizableWidget, ...]]:
    def create_buttons(panel: PanelOnScreen) -> tuple[_SizableWidget, ...]:
        widgets: list[_SizableWidget] = []
        for spec in specs:
            widget: _SizableWidget = widget_type(**spec)
            widgets.append(widget)
        return tuple(widgets)

    return create_buttons
