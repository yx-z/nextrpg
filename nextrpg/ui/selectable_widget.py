from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Self

from nextrpg.ui.widget import Widget

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class SelectableWidget(Widget):
    is_selected: bool = False

    @property
    def select(self) -> Self:
        return replace(self, is_selected=True)

    @property
    def deselect(self) -> Self:
        return replace(self, is_selected=False)
