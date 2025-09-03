from __future__ import annotations

from dataclasses import dataclass
from typing import Self, Text, override

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.text_group import TextGroup
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.ui.sizable_widget import SizableWidget
from nextrpg.ui.widget import WidgetOnScreen


@dataclass(frozen=True)
class LabelOnScreen(WidgetOnScreen):
    widget_input: Label

    def tick(self, time_delta: Millisecond) -> Self:
        return self

    @property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        # TODO - SizableWidgetOnScreen to extract common logic of coordinate

        if self.widget_input.coordinate:
            coordinate = self.widget_input.coordinate
        else:
            coordinate = self._get_on_screen(Coordinate)
        return self.widget_input.text.drawing_group.drawing_on_screens(
            coordinate
        )


@dataclass(frozen=True, kw_only=True)
class Label(SizableWidget[LabelOnScreen]):
    message: str | Text | TextGroup

    @override
    @property
    def size(self) -> Size:
        return self.text.size

    @property
    def text(self) -> Text | TextGroup:
        if isinstance(self.message, str):
            return Text(self.message)
        return self.message
