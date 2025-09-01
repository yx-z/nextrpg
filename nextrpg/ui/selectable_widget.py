from abc import abstractmethod
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Self, override

from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.ui.widget import Widget

if TYPE_CHECKING:
    from nextrpg.ui.selectable_widget_on_screen import SelectableWidgetOnScreen


@dataclass(frozen=True)
class SelectableWidget(Widget):
    is_selected: bool = False

    @property
    def select(self) -> Self:
        return replace(self, is_selected=True)

    @property
    def deselect(self) -> Self:
        return replace(self, is_selected=False)

    @override
    @abstractmethod
    def widget_on_screen(
        self, on_screen: dict[str, Coordinate | AreaOnScreen]
    ) -> SelectableWidgetOnScreen: ...
