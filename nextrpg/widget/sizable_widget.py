from abc import abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.sprite import Sprite
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.widget.widget import Widget

if TYPE_CHECKING:
    from nextrpg.widget.sizable_widget_spec import SizableWidgetSpec


@dataclass(frozen=True, kw_only=True)
class SizableWidget(Widget):
    spec: SizableWidgetSpec

    def anchored(
        self, coordinate: Coordinate, anchor: Anchor = Anchor.TOP_LEFT
    ) -> Self:
        spec = self.spec.anchored(coordinate, anchor)
        return replace(self, spec=spec)

    @override
    @cached_property
    def _drawing_on_screens_without_parent_and_animation(
        self,
    ) -> DrawingOnScreens:
        return self.sprite.drawing_on_screens(self.coordinate, self.spec.anchor)

    @cached_property
    def coordinate(self) -> Coordinate:
        if self.spec.coordinate:
            return self.spec.coordinate
        assert isinstance(
            self.on_screen, Coordinate
        ), f"Expect a point/Coordinate for {self.spec.name}. Got {self.on_screen}."
        return self.on_screen

    @property
    @abstractmethod
    def sprite(self) -> Sprite: ...
