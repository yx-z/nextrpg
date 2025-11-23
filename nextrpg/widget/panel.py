from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import ClassVar, override

from nextrpg import Anchor
from nextrpg.config.config import config
from nextrpg.config.widget.panel_config import PanelConfig
from nextrpg.core.dataclass_with_default import (
    private_init_below,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.widget.sizable_widget import SizableWidget, SizableWidgetOnScreen
from nextrpg.widget.widget import Widget, WidgetOnScreen
from nextrpg.widget.widget_group import WidgetGroup, WidgetGroupOnScreen


@dataclass(frozen=True, kw_only=True)
class PanelOnScreen(WidgetGroupOnScreen):
    widget: Panel
    _: KW_ONLY = private_init_below()
    _visible: range = ...

    @cached_property
    def children_drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens = [
            drawing_on_screen
            for i, child in enumerate(self._children)
            if i in self._visible
            for drawing_on_screen in child._drawing_on_screens_without_parent
        ]
        if self._visible.start != 0:
            icon = self.widget.config.more_above_icon.drawing_on_screen(
                self.area.top_center, Anchor.BOTTOM_CENTER
            )
            drawing_on_screens.append(icon)
        if self._visible.stop != len(self._children):
            icon = self.widget.config.more_below_icon.drawing_on_screen(
                self.area.bottom_center, Anchor.TOP_CENTER
            )
            drawing_on_screens.append(icon)
        return tuple(drawing_on_screens)

    @cached_property
    def area(self) -> AreaOnScreen:
        assert isinstance(
            self.on_screen, AreaOnScreen
        ), f"Expect AreaOnScreen for {self.widget.name}. Got {self.on_screen}."
        return self.on_screen

    @override
    def _init_children(
        self, children: tuple[Widget, ...]
    ) -> tuple[WidgetOnScreen, ...]:
        res: list[WidgetOnScreen] = []
        for i, widget_on_screen in enumerate(super()._init_children(children)):
            if (
                isinstance(widget_on_screen, SizableWidgetOnScreen)
                and not (widget := widget_on_screen.widget).coordinate
            ):
                widget = self._anchor(i, widget)
                anchored = replace(widget_on_screen, widget=widget)
            else:
                anchored = widget_on_screen
            res.append(anchored)
        return tuple(res)

    def _anchor[_SizableWidget: SizableWidget](
        self, i: int, widget: _SizableWidget
    ) -> _SizableWidget:
        padding = self.widget.config.children_padding
        top_left = ...
        return widget.anchored(top_left)


@dataclass(frozen=True, kw_only=True)
class Panel(WidgetGroup[PanelOnScreen]):
    name: str
    children: tuple[Widget, ...]
    config: PanelConfig = field(default_factory=lambda: config().widget.panel)
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = PanelOnScreen
