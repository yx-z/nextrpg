from dataclasses import KW_ONLY, dataclass, replace
from typing import Any, Self, override

from nextrpg import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.fade import FadeIn, Resource
from nextrpg.scene.eventful_scene import BackgroundEvent, RpgEventScene
from nextrpg.scene.scene import Scene


@dataclass_with_instance_init(frozen=True)
class FadeInScene(RpgEventScene):
    resource: Resource
    wait: bool = True
    duration: Millisecond | None = None
    _: KW_ONLY = not_constructor_below()
    _fade: FadeIn = instance_init(
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
            return replace(ticked, fade=fade)

        background_fade_in = BackgroundFadeIn(fade=fade)
        return ticked.scene.complete(
            self.generator,
            event_result=background_fade_in.sentinel,
            background_event=background_fade_in,
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


@register_rpg_event
def fade_in(
    resource: Resource, duration: Millisecond | None = None, wait: bool = True
) -> None:
    return lambda generator, scene: FadeInScene(
        generator, scene, resource, duration, wait=wait
    )
