from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import ClassVar, override

from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.geometry.dimension import Size
from nextrpg.widget.sizable_widget import (
    SizableWidget,
    SizableWidgetOnScreen,
)


@dataclass(frozen=True)
class LabelOnScreen(SizableWidgetOnScreen):
    widget: Label

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        return self.widget.text.drawing


@dataclass(frozen=True, kw_only=True)
class Label(SizableWidget):
    message: str | Text | TextGroup
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = LabelOnScreen

    @override
    @cached_property
    def size(self) -> Size:
        return self.text.size

    @cached_property
    def text(self) -> Text | TextGroup:
        if isinstance(self.message, str):
            return Text(self.message)
        return self.message
