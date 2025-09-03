from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Self, TypeVar

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate


@dataclass(frozen=True)
class WidgetOnScreen(ABC):
    widget_input: Widget
    name_to_on_screens: dict[str, Coordinate | AreaOnScreen]

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    def _get_on_screen[T](self, cls: type[T]) -> T:
        name = getattr(self.widget_input, "name", None)
        assert name, f"Require 'name' attribute for widget {self.widget_input}."
        obj = self.name_to_on_screens.get(name)
        assert isinstance(
            obj, cls
        ), f"Require {cls.__name__} for {name}. Got {obj}."
        return obj


_WidgetOnScreen = TypeVar("_WidgetOnScreen", bound=WidgetOnScreen)


@dataclass(frozen=True)
class Widget[_WidgetOnScreen](ABC):
    widget_on_screen_type: ClassVar[type]

    def widget_on_screen(
        self, name_to_on_screens: dict[str, Coordinate | AreaOnScreen]
    ) -> _WidgetOnScreen:
        return self.widget_on_screen_type(
            widget_input=self, name_to_on_screens=name_to_on_screens
        )
