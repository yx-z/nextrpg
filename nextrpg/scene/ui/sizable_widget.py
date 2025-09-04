from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, TypeVar, override

from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.scene.ui.widget import Widget, WidgetOnScreen


@dataclass(frozen=True, kw_only=True)
class SizableWidgetOnScreen(WidgetOnScreen):
    widget_input: SizableWidget

    @override
    @cached_property
    def drawing_on_screens_after_parent(self) -> tuple[DrawingOnScreen, ...]:
        if self.widget_input.coordinate:
            coordinate = self.widget_input.coordinate
        else:
            coordinate = self.from_on_screen(Coordinate)

        if isinstance(self.drawing, Drawing):
            return (self.drawing.drawing_on_screen(coordinate),)
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
