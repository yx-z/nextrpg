from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, field
from functools import cached_property
from typing import ClassVar, override

from nextrpg import WidgetOnScreen
from nextrpg.config.config import config
from nextrpg.config.widget.panel_config import PanelConfig
from nextrpg.core.dataclass_with_default import (
    private_init_below,
)
from nextrpg.geometry.area_on_screen import AreaOnScreen
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

    @override
    def init_children(
        self,
        children: (
            tuple[Widget | WidgetOnScreen, ...]
            | Callable[
                [WidgetGroupOnScreen], tuple[Widget | WidgetOnScreen, ...]
            ]
        ),
    ) -> tuple[WidgetOnScreen, ...]:
        return ()


@dataclass(frozen=True, kw_only=True)
class Panel(WidgetGroup[PanelOnScreen]):
    name: str
    children: tuple[Widget, ...] | Callable[[PanelOnScreen], tuple[Widget, ...]]
    config: PanelConfig = field(default_factory=lambda: config().widget.panel)
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = PanelOnScreen
