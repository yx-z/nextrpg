from collections.abc import Callable
from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import ClassVar, Self, override

from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.event.io_event import IoEvent, KeyboardKey, is_key_press
from nextrpg.geometry.dimension import Size
from nextrpg.scene.scene import Scene
from nextrpg.widget.sizable_widget import (
    SizableWidget,
    SizableWidgetOnScreen,
)
from nextrpg.widget.widget import Widget


@dataclass_with_default(frozen=True, kw_only=True)
class ButtonOnScreen(SizableWidgetOnScreen):
    widget: Button

    @override
    @cached_property
    def drawing(self) -> AnimationLike:
        if self._is_selected:
            return self.widget.active
        return self.widget.idle

    @override
    def _event_after_selected(self, event: IoEvent) -> Scene:
        if not is_key_press(event, KeyboardKey.CONFIRM):
            return self

        if callable(self.widget.on_click):
            self.widget.on_click()
            return self

        if isinstance(self.widget.on_click, Widget):
            return self.widget.on_click.widget_on_screen(
                self.name_to_on_screens, self.parent
            ).select

        return self.widget.on_click

    @override
    def _tick_after_parent(self, time_delta: Millisecond) -> Self:
        if self._is_selected:
            active = self.widget.active.tick(time_delta)
            idle = self.widget.idle
        else:
            active = self.widget.active
            idle = self.widget.idle.tick(time_delta)
        widget = replace(self.widget, idle=idle, active=active)
        return replace(self, widget=widget)


@dataclass_with_default(frozen=True, kw_only=True)
class Button(SizableWidget):
    name: str
    on_click: Scene | Widget | Callable[[], None]
    idle: AnimationLike
    active: AnimationLike
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = ButtonOnScreen

    @override
    @cached_property
    def size(self) -> Size:
        return self.idle.size
