from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene
from nextrpg.ui.button import Button
from nextrpg.ui.selectable_widget_on_screen import SelectableWidgetOnScreen


@dataclass(frozen=True)
class ButtonOnScreen(SelectableWidgetOnScreen):
    widget: Button

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self.widget.is_selected:
            drawings = self.widget.selected
        else:
            drawings = self.widget.idle

        assert isinstance(
            coordinate := self.name_to_on_screens[self.widget.unique_name],
            Coordinate,
        ), f"Button {self.widget.unique_name} requires on_screen as a coordinate"

        if isinstance(drawings, Drawing):
            return (drawings.drawing_on_screen(coordinate),)
        return drawings.drawing_on_screens(coordinate)

    @override
    def selected_event(
        self, event: IoEvent
    ) -> Scene | SelectableWidgetOnScreen | None:
        if isinstance(event, KeyPressDown) and event.key is KeyboardKey.CONFIRM:
            if callable(self.widget.on_click):
                self.widget.on_click()
                return self
            return self.widget.on_click
        return self
