from dataclasses import KW_ONLY, dataclass, field, replace
from typing import Self, override

from nextrpg.animation.fade import FadeOut
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
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
class BackgroundFadeOutEvent(BackgroundEvent):
    fade: FadeOut

    @override
    @property
    def draw_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.fade.drawing_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, fade=self.fade.tick(time_delta))

    @property
    @override
    def complete(self) -> bool:
        return self.fade.is_complete


@dataclass_with_default(frozen=True)
class FadeOutEventScene(RpgEventScene[BackgroundFadeOutEvent]):
    sentinel: BackgroundEventSentinel
    wait: bool = True
    duration: Millisecond = field(
        default_factory=lambda: config().timing.fade_duration
    )
    _: KW_ONLY = private_init_below()
    _fade: FadeOut = default(lambda self: self._init_fade)

    @property
    @override
    def add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade.drawing_on_screens

    @override
    def tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        fade = self._fade.tick(time_delta)
        background_removed = ticked.scene.remove_background_event(self.sentinel)
        if not self.wait:
            background_event = BackgroundFadeOutEvent(fade=fade)
            return background_removed.is_complete(
                self.generator, background_event=background_event
            )

        if fade.is_complete:
            return background_removed.is_complete(self.generator)

        return replace(ticked, scene=background_removed, _fade=fade)

    @property
    def _init_fade(self) -> FadeOut:
        resource = self.scene.get_background_event(
            self.sentinel
        ).draw_on_screens
        return FadeOut(resource, self.duration)


@register_rpg_event_scene(FadeOutEventScene)
def fade_out(
    sentinel: BackgroundEventSentinel,
    wait: bool = True,
    duration: Millisecond | None = None,
) -> None: ...
