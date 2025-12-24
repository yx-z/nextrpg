from abc import abstractmethod
from dataclasses import dataclass, replace
from typing import Self

from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Size
from nextrpg.widget.sizable_widget import SizableWidget
from nextrpg.widget.widget_spec import WidgetSpec


@dataclass(frozen=True)
class SizableWidgetSpec[_SizableWidget: SizableWidget](
    WidgetSpec[_SizableWidget]
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
