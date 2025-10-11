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
from nextrpg.event.io_event import IoEvent, KeyboardKey, is_key_press
from nextrpg.scene.scene import Scene
from nextrpg.scene.widget.widget_group import WidgetGroupOnScreen

if TYPE_CHECKING:
    from nextrpg.scene.map.map_scene import MapScene


@dataclass_with_default(frozen=True)
class MenuScene(Scene):
    map: MapScene
    widget: WidgetGroupOnScreen
    config: MenuConfig = field(default_factory=lambda: config().menu)
    _: KW_ONLY = private_init_below()
    _parent: MapScene = default(lambda self: self.map.stop_player)
    _fade_in: FadeIn = default(
        lambda self: FadeIn(
            DrawingOnScreens(
                self._parent.drawing_on_screens
            ).drawing_on_screen.blur(self.config.blur_radius),
            self.config.fade_duration,
        )
    )
    _fade_out: FadeOut | None = None

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if not (fade_in := self._fade_in.tick(time_delta)).is_complete:
            return replace(self, _fade_in=fade_in)

        if not self._fade_out:
            widget = self.widget.tick(time_delta)
            return replace(self, _fade_in=fade_in, widget=widget)

        if not (fade_out := self._fade_out.tick(time_delta)).is_complete:
            return replace(self, _fade_out=fade_out)
        return self._parent

    @override
    def event(self, event: IoEvent) -> Scene:
        if not self._fade_in.is_complete:
            return self

        if not self._fade_out:
            if is_key_press(event, KeyboardKey.CANCEL):
                fade_out = FadeOut(
                    self._fade_in.resource, self.config.fade_duration
                )
                return replace(self, _fade_out=fade_out)
            if isinstance(res := self.widget.event(event), WidgetGroupOnScreen):
                return replace(self, widget=res)
            return res

        return self

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if not self._fade_in.is_complete:
            return (
                self._parent.drawing_on_screens
                + self._fade_in.drawing_on_screens
            )

        if not self._fade_out:
            return (
                self._fade_in.drawing_on_screens
                + self.widget.drawing_on_screens
            )

        return (
            self._parent.drawing_on_screens + self._fade_out.drawing_on_screens
        )
