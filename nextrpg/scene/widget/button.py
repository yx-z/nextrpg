from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import ClassVar, Self, override

from nextrpg.animation.abstract_animation import AbstractAnimation
from nextrpg.core.dataclass_with_default import dataclass_with_default
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.event.io_event import IoEvent, KeyboardKey, is_key_press
from nextrpg.geometry.dimension import Size
from nextrpg.scene.scene import Scene
from nextrpg.scene.widget.sizable_widget import (
    SizableWidget,
    SizableWidgetOnScreen,
)
from nextrpg.scene.widget.widget import Widget


@dataclass_with_default(frozen=True, kw_only=True)
class ButtonOnScreen(SizableWidgetOnScreen):
    widget: Button

    @override
    @property
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
        if isinstance(self.widget.idle, AbstractAnimation):
            idle = self.widget.idle.tick(time_delta)
        else:
            idle = self.widget.idle

        if isinstance(self.widget.active, AbstractAnimation):
            active = self.widget.active.tick(time_delta)
        else:
            active = self.widget.active

        widget = replace(self.widget, idle=idle, active=active)
        return replace(self, widget=widget)


@dataclass(frozen=True, kw_only=True)
class Button(SizableWidget[ButtonOnScreen]):
    name: str
    idle: AnimationLike
    active: AnimationLike
    on_click: Scene | Widget | Callable[[], None]
    widget_on_screen_type: ClassVar[type[ButtonOnScreen]] = ButtonOnScreen

    @override
    @property
    def size(self) -> Size:
        return self.idle.size
