from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Self, override

from nextrpg.animation.animation import Animation
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene
from nextrpg.ui.selectable_widget import SelectableWidget

if TYPE_CHECKING:
    from nextrpg.ui.button_on_screen import ButtonOnScreen


@dataclass(frozen=True, kw_only=True)
class Button(SelectableWidget):
    unique_name: str
    idle: Drawing | DrawingGroup | Animation
    selected: Drawing | DrawingGroup | Animation
    confirm: Scene | Callable[[], None]

    @override
    def widget_on_screen(
        self, on_screen: dict[str, Coordinate | AreaOnScreen]
    ) -> ButtonOnScreen:
        from nextrpg.ui.button_on_screen import ButtonOnScreen

        return ButtonOnScreen(self, on_screen)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if isinstance(self.idle, Animation):
            idle = self.idle.tick(time_delta)
        else:
            idle = self.idle

        if isinstance(self.selected, Animation):
            selected = self.selected.tick(time_delta)
        else:
            selected = self.selected

        return replace(self, idle=idle, selected=selected)
