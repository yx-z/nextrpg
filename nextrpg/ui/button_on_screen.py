from dataclasses import dataclass
from functools import cached_property
from typing import Self, override

from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyPressDown, KeyboardKey
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
            coordinate := self.on_screen[self.widget.unique_name], Coordinate
        ), f"Button {self.widget.unique_name} requires on_screen as a coordinate"

        if isinstance(drawings, Drawing):
            return (drawings.drawing_on_screen(coordinate),)
        return drawings.drawing_on_screens(coordinate)

    @override
    def event(self, event: IoEvent) -> Scene | Self | None:
        if (
            self.widget.is_selected
            and isinstance(event, KeyPressDown)
            and event.key is KeyboardKey.CONFIRM
        ):
            if callable(self.widget.confirm):
                self.widget.confirm()
                return self
            return self.widget.confirm
        return self
