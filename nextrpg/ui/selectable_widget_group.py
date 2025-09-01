from dataclasses import dataclass, replace
from enum import Enum, auto
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg.core.time import Millisecond
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.ui.selectable_widget import SelectableWidget

if TYPE_CHECKING:
    from nextrpg.ui.selectable_widget_group_on_screen import (
        SelectableWidgetGroupOnScreen,
    )


class ScrollDirection(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()


@dataclass(frozen=True, kw_only=True)
class SelectableWidgetGroup(SelectableWidget):
    widgets: tuple[SelectableWidget, ...]
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True

    @override
    @cached_property
    def select(self) -> Self:
        return self._deselect_and_select(0)

    @cached_property
    def select_next(self) -> Self:
        assert self._selected_index is not None
        if (next_index := self._selected_index + 1) == len(self.widgets):
            if self.loop:
                next_index = 0
            else:
                return self
        return self._deselect_and_select(next_index)

    @cached_property
    def select_previous(self) -> Self:
        assert self._selected_index is not None
        if (previous_index := self._selected_index - 1) == -1:
            if self.loop:
                previous_index = len(self.widgets) - 1
            else:
                return self
        return self._deselect_and_select(previous_index)

    @override
    def widget_on_screen(
        self, name_to_on_screens: dict[str, Coordinate | AreaOnScreen]
    ) -> SelectableWidgetGroupOnScreen:
        from nextrpg.ui.selectable_widget_group_on_screen import (
            SelectableWidgetGroupOnScreen,
        )

        return SelectableWidgetGroupOnScreen(self, name_to_on_screens)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        widgets = tuple(w.tick(time_delta) for w in self.widgets)
        return replace(self, widgets=widgets)

    @cached_property
    def _selected_index(self) -> int | None:
        for i, widget in enumerate(self.widgets):
            if widget.is_selected:
                return i
        return None

    def _deselect_and_select(self, selected_index: int) -> Self:
        widgets: list[SelectableWidget] = []
        for i, widget in enumerate(self.widgets):
            if i == selected_index:
                res = widget.select
            elif i == self._selected_index:
                res = widget.deselect
            else:
                res = widget
            widgets.append(res)
        return replace(self, is_selected=True, widgets=tuple(widgets))
