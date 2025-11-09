from abc import abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.geometry.anchor import Anchor
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
    ) -> list[DrawingOnScreen]:
        return self.drawing.drawing_on_screens(
            self.coordinate, self.widget.anchor
        )

    @cached_property
    def coordinate(self) -> Coordinate:
        if self.widget.coordinate:
            return self.widget.coordinate
        return self.from_on_screen(Coordinate)

    @property
    @abstractmethod
    def drawing(self) -> AnimationLike: ...


@dataclass(frozen=True)
class SizableWidget[_SizableWidgetOnScreen: SizableWidgetOnScreen](
    Widget[_SizableWidgetOnScreen]
):
    coordinate: Coordinate | None = None
    anchor: Anchor = Anchor.TOP_LEFT

    def anchored(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> Self:
        return replace(self, coordinate=coordinate, anchor=anchor)

    @property
    @abstractmethod
    def size(self) -> Size: ...
