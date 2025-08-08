from dataclasses import KW_ONLY, dataclass, replace
from typing import Self, override

from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.fade import FadeIn, Resource
from nextrpg.scene.rpg_event.eventful_scene import (
    BackgroundEvent,
    BackgroundEventSentinel,
    RpgEventScene,
    register_rpg_event_scene,
)
from nextrpg.scene.scene import Scene


@dataclass_with_init(frozen=True)
class FadeInScene(RpgEventScene[BackgroundEventSentinel]):
    resource: Resource
    wait: bool = True
    duration: Millisecond | None = None
    _: KW_ONLY = not_constructor_below()
    _fade: FadeIn = default(
        lambda self: (
            FadeIn(self.resource)
            if self.duration is None
            else FadeIn(self.resource, self.duration)
        )
    )

    @property
    @override
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return self._fade.draw_on_screens

    @override
    def post_tick(self, time_delta: Millisecond, ticked: Self) -> Scene:
        fade = self._fade.tick(time_delta)
        if self.wait and not fade.complete:
            return replace(ticked, _fade=fade)

        background_fade_in = BackgroundFadeIn(fade=fade)
        return ticked.scene.complete(
            self.generator, background_fade_in.sentinel, background_fade_in
        )


@dataclass(frozen=True, kw_only=True)
class BackgroundFadeIn(BackgroundEvent):
    fade: FadeIn

    @property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self.fade.draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, fade=self.fade.tick(time_delta))

    @property
    @override
    def complete(self) -> bool:
        return False


@register_rpg_event_scene(FadeInScene)
def fade_in(
    resource: Resource, wait: bool = True, duration: Millisecond | None = None
) -> BackgroundEventSentinel: ...
