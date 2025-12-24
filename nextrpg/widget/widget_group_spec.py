from dataclasses import KW_ONLY, dataclass
from typing import ClassVar

from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.widget_group import WidgetGroup
from nextrpg.widget.widget_spec import WidgetSpec


@dataclass(frozen=True, kw_only=True)
class WidgetGroupSpec[_WidgetGroup: WidgetGroup](WidgetSpec[_WidgetGroup]):
    widgets: WidgetSpec | tuple[WidgetSpec, ...]
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True
    _: KW_ONLY = private_init_below()
    widget_type: ClassVar[type] = WidgetGroup
