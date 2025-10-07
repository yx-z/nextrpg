from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.event.io_event import IoEvent
from nextrpg.scene.scene import Scene

if TYPE_CHECKING:
    from nextrpg.scene.map.map_scene import MapScene


@dataclass(frozen=True)
class MenuScene(Scene):
    scene: MapScene

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        scene = self.scene.tick_without_event(time_delta)
        return replace(self, scene=scene)

    def event(self, event: IoEvent) -> Self:
        scene = self.scene.event(event)
        return replace(self, scene=scene)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens = DrawingOnScreens(
            self.scene.drawing_on_screens_before_shift
        )
        blurred = (
            drawing_on_screens.drawing_on_screen.blur(2)
            + self.scene.drawing_on_screens_shift
            - drawing_on_screens.top_left
        )
        return (blurred,)
