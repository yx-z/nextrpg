from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg import TmxWidgetGroupOnScreen
from nextrpg.config.config import config
from nextrpg.config.menu_config import MenuConfig
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.scene.scene import Scene

if TYPE_CHECKING:
    from nextrpg.scene.map.map_scene import MapScene


@dataclass(frozen=True)
class MenuScene(Scene):
    scene: MapScene
    tmx: TmxWidgetGroupOnScreen
    config: MenuConfig = field(default_factory=lambda: config().menu)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        scene = self.scene.tick_without_event(time_delta)
        return replace(self, scene=scene)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens = DrawingOnScreens(self.scene.drawing_on_screens)
        blurred = drawing_on_screens.drawing_on_screen.blur(
            self.config.blur_radius
        )
        shifted = blurred - drawing_on_screens.top_left
        return (shifted,)
