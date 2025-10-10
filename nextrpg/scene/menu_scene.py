from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg.animation.abstract_animation_on_screen import (
    AbstractAnimationOnScreen,
)
from nextrpg.animation.fade import FadeIn
from nextrpg.config.config import config
from nextrpg.config.menu_config import MenuConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.scene.scene import Scene
from nextrpg.scene.widget.tmx_widget_group_on_screen import (
    TmxWidgetGroupOnScreen,
)

if TYPE_CHECKING:
    from nextrpg.scene.map.map_scene import MapScene


@dataclass_with_default(frozen=True)
class MenuScene(Scene):
    scene: MapScene
    tmx: TmxWidgetGroupOnScreen
    config: MenuConfig = field(default_factory=lambda: config().menu)
    _: KW_ONLY = private_init_below()
    _animation: AbstractAnimationOnScreen = default(
        lambda self: FadeIn(self._scene_drawing, self.config.fade_duration)
    )

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self._animation.is_complete:
            tmx = self.tmx.tick(time_delta)
            return replace(self, tmx=tmx)
        animation = self._animation.tick(time_delta)
        return replace(self, _animation=animation)

    @override
    def event(self, event: IoEvent) -> Scene:
        if not self._animation.is_complete:
            return self
        if isinstance(event, KeyPressDown) and event.key is KeyboardKey.CANCEL:
            return self.scene
        if isinstance(res := self.tmx.event(event), TmxWidgetGroupOnScreen):
            return replace(self, tmx=res)
        return res

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self._animation.is_complete:
            return (
                self._animation.drawing_on_screens + self.tmx.drawing_on_screens
            )
        return (
            self.scene.drawing_on_screens + self._animation.drawing_on_screens
        )

    @property
    def _scene_drawing(self) -> DrawingOnScreen:
        drawing_on_screens = DrawingOnScreens(self.scene.drawing_on_screens)
        return drawing_on_screens.drawing_on_screen.blur(
            self.config.blur_radius
        )
