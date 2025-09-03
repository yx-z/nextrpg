from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, replace
from typing import ClassVar, Self, TypeVar

from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.scene.scene import Scene
from nextrpg.ui.widget import Widget, WidgetOnScreen


@dataclass(frozen=True)
class SelectableWidgetOnScreen(WidgetOnScreen):
    is_selected: bool = False
    parent: SelectableWidgetOnScreen | None = None

    def set_parent(self, parent: SelectableWidgetOnScreen) -> Self:
        return replace(self, parent=parent)

    @property
    def select(self) -> Self:
        if self.parent:
            parent = self.parent.deselect
        else:
            parent = None
        return replace(self, is_selected=True, parent=parent)

    @property
    def deselect(self) -> Self:
        if self.parent:
            parent = self.parent.select
        else:
            parent = None
        return replace(self, is_selected=False, parent=parent)

    def event(self, event: IoEvent) -> SelectableWidgetOnScreen | Scene:
        if not self.is_selected:
            return self
        if isinstance(event, KeyPressDown) and event.key is KeyboardKey.CANCEL:
            if self.parent:
                return self.parent
            return self
        return self.selected_event(event)

    @abstractmethod
    def selected_event(
        self, event: IoEvent
    ) -> SelectableWidgetOnScreen | Scene: ...


_SelectableWidgetOnScreen = TypeVar(
    "_SelectableWidgetOnScreen", bound=SelectableWidgetOnScreen
)


@dataclass(frozen=True)
class SelectableWidget(Widget[_SelectableWidgetOnScreen]):
    widget_on_screen_type: ClassVar[type[SelectableWidgetOnScreen]]
