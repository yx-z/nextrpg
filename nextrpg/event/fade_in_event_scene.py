from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.fade import FadeIn
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import (
    AnimationOnScreenLike,
    animate,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.event.background_event import (
    BackgroundEvent,
    BackgroundEventSentinel,
)
from nextrpg.event.rpg_event_scene import (
    RpgEventScene,
    register_rpg_event_scene,
)
from nextrpg.scene.scene import Scene


@dataclass(frozen=True, kw_only=True)
class BackgroundFadeInEvent(BackgroundEvent):
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
        return False


@dataclass_with_default(frozen=True)
class FadeInEventScene(RpgEventScene):
    resource: AnimationOnScreenLike
    wait: bool = True
    duration: Millisecond = field(
        default_factory=lambda: config().animation.default_timed_animation_duration
    )
    _: KW_ONLY = private_init_below()
    _fade: TimedAnimationOnScreens = default(
        lambda self: animate(self.resource, FadeIn, duration=self.duration)
    )

    @override
    @cached_property
    def drawing_on_screens_after_parent(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade.drawing_on_screens

    @override
    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self
    ) -> Scene:
        fade = self._fade.tick(time_delta)
        if self.wait and not fade.is_complete:
            return replace(ticked, _fade=fade)

        background_fade_in = BackgroundFadeInEvent(fade=fade)
        return ticked.parent.complete(
            self.generator, background_fade_in.sentinel, background_fade_in
        )


@register_rpg_event_scene(FadeInEventScene)
def fade_in(
    resource: AnimationOnScreenLike,
    wait: bool = True,
    duration: Millisecond | None = None,
) -> BackgroundEventSentinel: ...
