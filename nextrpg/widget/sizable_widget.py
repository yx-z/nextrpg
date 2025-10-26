from abc import abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.widget.widget import Widget, WidgetOnScreen


@dataclass(frozen=True, kw_only=True)
class SizableWidgetOnScreen(WidgetOnScreen):
    widget: SizableWidget

    @override
    @cached_property
    def _drawing_on_screens_without_parent_and_animation(
        self,
    ) -> tuple[DrawingOnScreen, ...]:
        if self.widget.coordinate:
            coordinate = self.widget.coordinate
        else:
            coordinate = self.from_on_screen(Coordinate)
        return self.drawing.drawing_on_screens(coordinate)

    @property
    @abstractmethod
    def drawing(self) -> AnimationLike: ...


@dataclass(frozen=True)
class SizableWidget(Widget):
    coordinate: Coordinate | None = None

    def anchor(self, coordinate: Coordinate) -> Self:
        return replace(self, coordinate=coordinate)

    @property
    @abstractmethod
    def size(self) -> Size: ...
