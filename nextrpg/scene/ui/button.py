from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any, ClassVar, Self, override

from nextrpg.animation.animation import Animation
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.geometry.dimension import Size
from nextrpg.scene.scene import Scene
from nextrpg.scene.ui.sizable_widget import SizableWidget, SizableWidgetOnScreen
from nextrpg.scene.ui.widget import Widget


@dataclass_with_default(frozen=True, kw_only=True)
class ButtonOnScreen(SizableWidgetOnScreen):
    widget_input: Button
    _ = private_init_below()
    _button: Button = default(lambda self: self.widget_input)

    @override
    @property
    def drawing(self) -> Drawing | DrawingGroup:
        if self.is_selected:
            return self._button.selected
        return self._button.idle

    @override
    def event_after_selected(self, event: IoEvent) -> Scene:
        if (
            not isinstance(event, KeyPressDown)
            or event.key is not KeyboardKey.CONFIRM
        ):
            return self

        if callable(self._button.on_click):
            self._button.on_click()
            return self

        if isinstance(self._button.on_click, Widget):
            return self._button.on_click.widget_on_screen(
                self.name_to_on_screens, self.parent
            ).select

        return self._button.on_click

    @override
    def tick_after_parent(self, time_delta: Millisecond) -> Self:
        if isinstance(self._button.idle, Animation):
            idle = self._button.idle.tick(time_delta)
        else:
            idle = self._button.idle

        if isinstance(self._button.selected, Animation):
            active = self._button.selected.tick(time_delta)
        else:
            active = self._button.selected

        button = replace(self._button, idle=idle, active=active)
        return replace(self, _button=button)


@dataclass(frozen=True, kw_only=True)
class Button(SizableWidget[ButtonOnScreen]):
    name: str
    idle: Drawing | DrawingGroup | Animation
    selected: Drawing | DrawingGroup | Animation
    on_click: Scene | Widget | Callable[[], Any]
    widget_on_screen_type: ClassVar[type[ButtonOnScreen]] = ButtonOnScreen

    def __str__(self) -> str:
        return f"Button({self.name})"

    @override
    @property
    def size(self) -> Size:
        return self.idle.size
