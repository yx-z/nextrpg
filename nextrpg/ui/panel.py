from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import ClassVar, Self, override

from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.nine_slice import NineSlice
from nextrpg.event.io_event import IoEvent
from nextrpg.geometry.dimension import Pixel
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.scene.scene import Scene
from nextrpg.ui.selectable_widget import (
    SelectableWidget,
    SelectableWidgetOnScreen,
)
from nextrpg.ui.widget_group import WidgetGroup, WidgetGroupOnScreen


@dataclass_with_default(frozen=True, kw_only=True)
class PanelOnScreen(SelectableWidgetOnScreen):
    widget_input: Panel
    _: KW_ONLY = private_init_below()
    _group_on_screen: WidgetGroupOnScreen = default(
        lambda self: self.widget_input.group.widget_on_screen(
            self.name_to_on_screens
        )
    )

    @override
    def selected_event(
        self, event: IoEvent
    ) -> SelectableWidgetOnScreen | Scene:
        # TODO
        return self

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens = self._group_on_screen.drawing_on_screens
        if self.widget_input.background:
            rect = self._get_on_screen(RectangleAreaOnScreen)
            background = self.widget_input.background.stretch(rect.size)
            return (background,) + drawing_on_screens
        return drawing_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        group_on_screen = self._group_on_screen.tick(time_delta)
        return replace(self, _group_on_screen=group_on_screen)


@dataclass(frozen=True)
class Panel(SelectableWidget[PanelOnScreen]):
    name: str
    group: WidgetGroup
    padding: Pixel = field(default_factory=lambda: config().ui.padding)
    background: NineSlice | None = None
    widget_on_screen_type: ClassVar[type[PanelOnScreen]] = PanelOnScreen
