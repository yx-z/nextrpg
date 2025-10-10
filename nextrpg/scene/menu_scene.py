from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg.animation.fade import FadeIn, FadeOut
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
    _fade_in: FadeIn = default(
        lambda self: FadeIn(
            DrawingOnScreens(
                self.scene.drawing_on_screens
            ).drawing_on_screen.blur(self.config.blur_radius),
            self.config.fade_duration,
        )
    )
    _fade_out: FadeOut | None = None

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self._fade_in.is_complete:
            if self._fade_out:
                if (fade_out := self._fade_out.tick(time_delta)).is_complete:
                    return self.scene
                return replace(self, _fade_out=fade_out)
            tmx = self.tmx.tick(time_delta)
            return replace(self, tmx=tmx)
        fade_in = self._fade_in.tick(time_delta)
        return replace(self, _fade_in=fade_in)

    @property
    def fade_in_complete(self) -> Self:
        return replace(self, _fade_in=self._fade_in.complete)

    @override
    def event(self, event: IoEvent) -> Scene:
        if not self._fade_in.is_complete or self._fade_out:
            return self
        if isinstance(event, KeyPressDown) and event.key is KeyboardKey.CANCEL:
            fade_out = FadeOut(
                self._fade_in.resource, self.config.fade_duration
            )
            return replace(self, _fade_out=fade_out)
        if isinstance(res := self.tmx.event(event), TmxWidgetGroupOnScreen):
            return replace(self, tmx=res)
        return res

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self._fade_out:
            return (
                self.scene.drawing_on_screens
                + self._fade_out.drawing_on_screens
            )
        if self._fade_in.is_complete:
            return (
                self._fade_in.drawing_on_screens + self.tmx.drawing_on_screens
            )
        return self.scene.drawing_on_screens + self._fade_in.drawing_on_screens
