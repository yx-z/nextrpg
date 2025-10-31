from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import ClassVar

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
        return self.from_on_screen(AreaOnScreen)


@dataclass(frozen=True, kw_only=True)
class Panel(WidgetGroup):
    name: str
    children: tuple[Widget | Callable[[PanelOnScreen], Widget], ...]
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = PanelOnScreen
