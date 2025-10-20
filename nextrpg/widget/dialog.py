from dataclasses import KW_ONLY, dataclass
from typing import ClassVar

from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.widget.widget import Widget, WidgetOnScreen


class DialogOnScreen(WidgetOnScreen): ...


@dataclass(frozen=True)
class Dialog(Widget[DialogOnScreen]):
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = DialogOnScreen
