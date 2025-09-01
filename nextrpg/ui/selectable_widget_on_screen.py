from __future__ import annotations

from abc import abstractmethod

from nextrpg.event.io_event import IoEvent
from nextrpg.scene.scene import Scene
from nextrpg.ui.selectable_widget import SelectableWidget
from nextrpg.ui.widget_on_screen import WidgetOnScreen


class SelectableWidgetOnScreen(WidgetOnScreen):
    widget: SelectableWidget

    def event(self, event: IoEvent) -> SelectableWidgetOnScreen | Scene | None:
        if not self.widget.is_selected:
            return self
        return self.selected_event(event)

    @abstractmethod
    def selected_event(
        self, event: IoEvent
    ) -> SelectableWidgetOnScreen | Scene | None: ...
