from __future__ import annotations

from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from typing import ClassVar, Self, override

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
from nextrpg.ui.selectable_widget import (
    SelectableWidget,
    SelectableWidgetOnScreen,
)
from nextrpg.ui.sizable_widget import (
    SizableSelectableWidget,
    SizableWidgetOnScreen,
)


@dataclass_with_default(frozen=True, kw_only=True)
class ButtonOnScreen(SelectableWidgetOnScreen, SizableWidgetOnScreen):
    widget_input: Button
    _: KW_ONLY = private_init_below()
    _button: Button = default(lambda self: self.widget_input)

    @override
    @property
    def drawing(self) -> Drawing | DrawingGroup:
        if self.is_selected:
            return self._button.selected
        return self._button.idle

    @override
    def selected_event(
        self, event: IoEvent
    ) -> Scene | SelectableWidgetOnScreen:
        if isinstance(event, KeyPressDown) and event.key is KeyboardKey.CONFIRM:
            if callable(self._button.on_click):
                self._button.on_click()
                return self
            if isinstance(self._button.on_click, Scene):
                return self._button.on_click
            return self._button.on_click.widget_on_screen(
                self.name_to_on_screens
            )
        return self

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if isinstance(self._button.idle, Animation):
            idle = self._button.idle.tick(time_delta)
        else:
            idle = self._button.idle

        if isinstance(self._button.selected, Animation):
            selected = self._button.selected.tick(time_delta)
        else:
            selected = self._button.selected

        button = replace(self._button, idle=idle, selected=selected)
        return replace(self, _button=button)


@dataclass(frozen=True, kw_only=True)
class Button(SizableSelectableWidget[ButtonOnScreen]):
    name: str
    idle: Drawing | DrawingGroup | Animation
    selected: Drawing | DrawingGroup | Animation
    on_click: Scene | SelectableWidget | Callable[[], None]
    widget_on_screen_type: ClassVar[type[ButtonOnScreen]] = ButtonOnScreen

    @override
    @property
    def size(self) -> Size:
        return self.idle.size
