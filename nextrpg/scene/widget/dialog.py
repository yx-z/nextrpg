from dataclasses import dataclass
from typing import ClassVar

from nextrpg.scene.widget.widget import Widget, WidgetOnScreen


class DialogOnScreen(WidgetOnScreen): ...


@dataclass(frozen=True)
class Dialog(Widget[DialogOnScreen]):
    widget_on_screen_type: ClassVar[type] = DialogOnScreen
