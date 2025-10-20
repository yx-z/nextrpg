from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.fade import FadeOut
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import animate
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
    fade: TimedAnimationOnScreens

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.fade.drawing_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, fade=self.fade.tick(time_delta))

    @override
    @cached_property
    def is_complete(self) -> bool:
        return self.fade.is_complete


@dataclass_with_default(frozen=True)
class FadeOutEventScene(RpgEventScene):
    sentinel: BackgroundEventSentinel
    wait: bool = True
    duration: Millisecond = field(
        default_factory=lambda: config().timing.fade_duration
    )
    _: KW_ONLY = private_init_below()
    _fade: TimedAnimationOnScreens = default(lambda self: self._init_fade)

    @override
    @cached_property
    def add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade.drawing_on_screens

    @override
    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self
    ) -> Scene:
        fade = self._fade.tick(time_delta)
        background_removed = ticked.parent.remove_background_event(
            self.sentinel
        )
        if not self.wait:
            background_event = BackgroundFadeOutEvent(fade=fade)
            return background_removed.complete(
                self.generator, background_event=background_event
            )

        if fade.is_complete:
            return background_removed.complete(self.generator)

        return replace(ticked, scene=background_removed, _fade=fade)

    @cached_property
    def _init_fade(self) -> TimedAnimationOnScreens:
        resource = self.parent.get_background_event(
            self.sentinel
        ).drawing_on_screens
        return animate(resource, FadeOut, duration=self.duration)


@register_rpg_event_scene(FadeOutEventScene)
def fade_out(
    sentinel: BackgroundEventSentinel,
    wait: bool = True,
    duration: Millisecond | None = None,
) -> None: ...
