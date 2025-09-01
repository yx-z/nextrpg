from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Self

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.ui.widget import Widget


@dataclass(frozen=True)
class WidgetOnScreen(ABC):
    widget: Widget
    on_screen: dict[str, Coordinate | AreaOnScreen]

    def tick(self, time_delta: Millisecond) -> Self:
        widget = self.widget.tick(time_delta)
        return replace(self, widget=widget)

    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...
