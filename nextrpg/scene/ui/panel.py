from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import ClassVar, Self, override

from nextrpg.config.config import config
from nextrpg.config.ui_config import PanelConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.scene.ui.sizable_widget import SizableWidget, SizableWidgetOnScreen
from nextrpg.scene.ui.widget import Widget, WidgetOnScreen


@dataclass_with_default(frozen=True, kw_only=True)
class PanelOnScreen(WidgetOnScreen):
    widget_input: Panel
    _: KW_ONLY = private_init_below()
    _children: tuple[SizableWidgetOnScreen, ...] = default(
        lambda self: self._init_children
    )

    @override
    @cached_property
    def _drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens = tuple(
            drawing_on_screen
            for child in self._children
            for drawing_on_screen in child._drawing_on_screens
        )
        return (
            self.widget_input.config.drawing_on_screens(self.area)
            + drawing_on_screens
        )

    @override
    def _tick(self, time_delta: Millisecond) -> Self:
        children = tuple(child._tick(time_delta) for child in self._children)
        return replace(self, _children=children)

    @cached_property
    def area(self) -> RectangleAreaOnScreen:
        return self._get_on_screen(RectangleAreaOnScreen)

    @property
    def _init_children(self) -> tuple[SizableWidgetOnScreen, ...]:
        return (
            self.widget_input.children[0]
            .anchor(self.area.top_left)
            .widget_on_screen(self.name_to_on_screens),
        )


@dataclass(frozen=True, kw_only=True)
class Panel(Widget[PanelOnScreen]):
    name: str
    children: tuple[SizableWidget, ...]
    config: PanelConfig = field(default_factory=lambda: config().ui.panel)
    widget_on_screen_type: ClassVar[type[PanelOnScreen]] = PanelOnScreen
