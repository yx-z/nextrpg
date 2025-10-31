from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import ClassVar

from nextrpg.core.dataclass_with_default import (
    private_init_below,
)
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.widget import Widget
from nextrpg.widget.widget_group import WidgetGroupOnScreen


@dataclass(frozen=True, kw_only=True)
class PanelOnScreen(WidgetGroupOnScreen):
    widget: Panel

    @cached_property
    def area(self) -> AreaOnScreen:
        return self.from_on_screen(AreaOnScreen)


@dataclass(frozen=True, kw_only=True)
class Panel(Widget):
    name: str
    children: tuple[Widget | Callable[[PanelOnScreen], Widget], ...]
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = PanelOnScreen
