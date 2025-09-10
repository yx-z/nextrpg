from abc import abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, TypeVar, override

from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.scene.widget.widget import Widget, WidgetOnScreen


@dataclass(frozen=True, kw_only=True)
class SizableWidgetOnScreen(WidgetOnScreen):
    widget_input: SizableWidget

    @override
    @cached_property
    def _drawing_on_screens_after_parent(self) -> tuple[DrawingOnScreen, ...]:
        if self.widget_input.coordinate:
            coordinate = self.widget_input.coordinate
        else:
            coordinate = self.from_on_screen(Coordinate)
        return self.drawing.drawing_on_screens(coordinate)

    @property
    @abstractmethod
    def drawing(self) -> Drawing | DrawingGroup: ...


_SizableWidgetOnScreen = TypeVar(
    "_SizableWidgetOnScreen", bound=SizableWidgetOnScreen
)


@dataclass(frozen=True)
class SizableWidget(Widget[_SizableWidgetOnScreen]):
    coordinate: Coordinate | None = None

    def anchor(self, coordinate: Coordinate) -> Self:
        return replace(self, coordinate=coordinate)

    @property
    @abstractmethod
    def size(self) -> Size: ...
