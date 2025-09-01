from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from nextrpg.core.time import Millisecond
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate

if TYPE_CHECKING:
    from nextrpg.ui.widget_on_screen import WidgetOnScreen


@dataclass(frozen=True)
class Widget(ABC):
    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @abstractmethod
    def widget_on_screen(
        self, on_screen: dict[str, Coordinate | AreaOnScreen]
    ) -> WidgetOnScreen: ...
