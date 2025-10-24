from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import ClassVar, NoReturn

from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.widget import Widget, WidgetOnScreen
from nextrpg.widget.widget_group import WidgetGroup, WidgetGroupOnScreen


@dataclass_with_default(frozen=True, kw_only=True)
class PanelOnScreen(WidgetGroupOnScreen):
    widget: Panel
    _: KW_ONLY = private_init_below()
    _children: tuple[WidgetOnScreen, ...] = default(
        lambda self: self._init_children(self.widget.create_children(self.area))
    )

    @cached_property
    def area(self) -> AreaOnScreen:
        return self.from_on_screen(AreaOnScreen)


@dataclass(frozen=True, kw_only=True)
class Panel(Widget):
    name: str
    create_children: Callable[[AreaOnScreen], tuple[Widget, ...]]
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = PanelOnScreen

    @property
    def children(self) -> NoReturn:
        raise RuntimeError(
            "Panel has to create its children by calling create_children(panel_on_screen)."
        )
