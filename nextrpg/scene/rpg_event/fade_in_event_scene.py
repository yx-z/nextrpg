from dataclasses import KW_ONLY, dataclass, field, replace
from typing import Self, override

from nextrpg.animation.fade import FadeIn
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.background_event import (
    BackgroundEvent,
    BackgroundEventSentinel,
)
from nextrpg.scene.rpg_event.rpg_event_scene import (
    RpgEventScene,
    register_rpg_event_scene,
)
from nextrpg.scene.scene import Scene


@dataclass(frozen=True, kw_only=True)
class BackgroundFadeInEvent(BackgroundEvent):
    fade: FadeIn

    @property
    @override
    def draw_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.fade.drawing_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, fade=self.fade.tick(time_delta))

    @property
    @override
    def complete(self) -> bool:
        return False


@dataclass_with_default(frozen=True)
class FadeInEventScene(RpgEventScene[BackgroundEventSentinel]):
    drawing_on_screen: DrawingOnScreen | tuple[DrawingOnScreen, ...]
    wait: bool = True
    duration: Millisecond = field(
        default_factory=lambda: config().timing.fade_duration
    )
    _: KW_ONLY = private_init_below()
    _fade: FadeIn = default(
        lambda self: FadeIn(self.drawing_on_screen, self.duration)
    )

    @property
    @override
    def add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade.drawing_on_screens

    @override
    def tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        fade = self._fade.tick(time_delta)
        if self.wait and not fade.is_complete:
            return replace(ticked, _fade=fade)

        background_fade_in = BackgroundFadeInEvent(fade=fade)
        return ticked.scene.complete(
            self.generator, background_fade_in.sentinel, background_fade_in
        )


@register_rpg_event_scene(FadeInEventScene)
def fade_in(
    resource: DrawingOnScreen | tuple[DrawingOnScreen, ...],
    wait: bool = True,
    duration: Millisecond | None = None,
) -> BackgroundEventSentinel: ...
