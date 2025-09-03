from __future__ import annotations

from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
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
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene
from nextrpg.ui.selectable_widget import (
    SelectableWidget,
    SelectableWidgetOnScreen,
)


@dataclass_with_default(frozen=True, kw_only=True)
class ButtonOnScreen(SelectableWidgetOnScreen):
    widget_input: Button
    _: KW_ONLY = private_init_below()
    _button: Button = default(lambda self: self.widget_input)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self.is_selected:
            drawings = self._button.selected
        else:
            drawings = self._button.idle

        if self._button.coordinate:
            coordinate = self._button.coordinate
        else:
            coordinate = self._get_on_screen(Coordinate)

        if isinstance(drawings, Drawing):
            return (drawings.drawing_on_screen(coordinate),)
        return drawings.drawing_on_screens(coordinate)

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


@dataclass(frozen=True)
class Button(SelectableWidget[ButtonOnScreen]):
    name: str
    idle: Drawing | DrawingGroup | Animation
    selected: Drawing | DrawingGroup | Animation
    on_click: Scene | SelectableWidget | Callable[[], None]
    coordinate: Coordinate | None = None
    widget_on_screen_type: ClassVar[type[ButtonOnScreen]] = ButtonOnScreen
