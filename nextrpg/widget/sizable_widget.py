from abc import abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite import Sprite
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Size
from nextrpg.widget.widget import Widget, WidgetOnScreen


@dataclass(frozen=True, kw_only=True)
class SizableWidgetOnScreen(WidgetOnScreen):
    widget: SizableWidget

    def anchored(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> Self:
        widget = self.widget.anchored(coordinate, anchor)
        return replace(self, widget=widget)

    @override
    @cached_property
    def _drawing_on_screens_without_parent_and_animation(
        self,
    ) -> tuple[DrawingOnScreen, ...]:
        return self.drawing.drawing_on_screens(
            self.coordinate, self.widget.anchor
        )

    @cached_property
    def coordinate(self) -> Coordinate:
        if self.widget.coordinate:
            return self.widget.coordinate
        assert isinstance(
            self.on_screen, Coordinate
        ), f"Expect a point/Coordinate for {self.widget.name}. Got {self.on_screen}."
        return self.on_screen

    @property
    @abstractmethod
    def drawing(self) -> Sprite: ...


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
