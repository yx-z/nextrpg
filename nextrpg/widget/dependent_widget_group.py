from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass
from typing import ClassVar, NoReturn

from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.widget import Widget, WidgetOnScreen
from nextrpg.widget.widget_group import WidgetGroupOnScreen


@dataclass_with_default(frozen=True)
class DependentWidgetGroupOnScreen(WidgetGroupOnScreen):
    widget: DependentWidgetGroup
    _: KW_ONLY = private_init_below()
    _children: tuple[WidgetOnScreen, ...] = default(
        lambda self: self._init_children(self._init_widgets)
    )

    @property
    def _init_widgets(self) -> tuple[Widget, ...]:
        widget_on_screens = tuple(
            widget.widget_on_screen(self.name_to_on_screens, self)
            for widget in self.widget.dependencies
        )
        return self.widget.create_widget(widget_on_screens)


@dataclass(frozen=True, kw_only=True)
class DependentWidgetGroup(Widget):
    create_widget: Callable[*tuple[WidgetOnScreen, ...], tuple[Widget, ...]]
    dependencies: tuple[Widget, ...]
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = DependentWidgetGroupOnScreen

    @property
    def children(self) -> NoReturn:
        raise RuntimeError(
            f"DependentWidgetGroup has to create its children by calling {self.create_widget}, after creating WidgetOnScreen for its dependencies {self.dependencies}."
        )
