from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.scene.scene import Scene
from nextrpg.ui.selectable_widget import SelectableWidget
from nextrpg.ui.selectable_widget_group import (
    ScrollDirection,
    SelectableWidgetGroup,
)
from nextrpg.ui.selectable_widget_on_screen import SelectableWidgetOnScreen


@dataclass(frozen=True)
class SelectableWidgetGroupOnScreen(SelectableWidgetOnScreen):
    widget: SelectableWidgetGroup

    @override
    def selected_event(self, event: IoEvent) -> Self | Scene | None:
        widgets: list[SelectableWidget] = []
        for widget in self._selectable_widget_on_screens:
            if res := widget.event(event):
                if isinstance(res, Scene):
                    return res
                widgets.append(res.widget)

        widget_group = replace(self.widget, widgets=tuple(widgets))
        if not isinstance(event, KeyPressDown):
            return replace(self, widget=widget_group)

        match self.widget.scroll_direction:
            case ScrollDirection.HORIZONTAL:
                match event.key:
                    case KeyboardKey.LEFT:
                        widget_group = widget_group.select_previous
                    case KeyboardKey.RIGHT:
                        widget_group = widget_group.select_next
            case ScrollDirection.VERTICAL:
                match event.key:
                    case KeyboardKey.UP:
                        widget_group = widget_group.select_previous
                    case KeyboardKey.DOWN:
                        widget_group = widget_group.select_next
        return replace(self, widget=widget_group)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return tuple(
            drawing_on_screen
            for widget in self._selectable_widget_on_screens
            for drawing_on_screen in widget.drawing_on_screens
        )

    @cached_property
    def _selectable_widget_on_screens(
        self,
    ) -> tuple[SelectableWidgetOnScreen, ...]:
        return tuple(
            widget.widget_on_screen(self.on_screen)
            for widget in self.widget.widgets
        )
