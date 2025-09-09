from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, override

from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.geometry.dimension import Size
from nextrpg.scene.widget.sizable_widget import (
    SizableWidget,
    SizableWidgetOnScreen,
)


@dataclass(frozen=True)
class LabelOnScreen(SizableWidgetOnScreen):
    widget_input: Label

    @override
    @property
    def drawing(self) -> DrawingGroup:
        return self.widget_input.text.drawing_group


@dataclass(frozen=True, kw_only=True)
class Label(SizableWidget[LabelOnScreen]):
    message: str | Text | TextGroup
    widget_on_screen_type: ClassVar[type[LabelOnScreen]] = LabelOnScreen

    @override
    @property
    def size(self) -> Size:
        return self.text.size

    @property
    def text(self) -> Text | TextGroup:
        if isinstance(self.message, str):
            return Text(self.message)
        return self.message
