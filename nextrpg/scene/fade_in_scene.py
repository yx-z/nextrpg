from dataclasses import KW_ONLY, dataclass, replace
from typing import Self, override

from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.fade import FadeIn
from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.scene.eventful_scene import BackgroundEvent, RpgEventScene
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class FadeInScene(RpgEventScene):
    fade: FadeIn
    _: KW_ONLY
    wait: bool

    @property
    @override
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return self.fade.draw_on_screens

    @override
    def post_tick(self, time_delta: Millisecond, ticked: Self) -> Scene:
        fade = self.fade.tick(time_delta)
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
def fade_in(fade: FadeIn, /, *, wait: bool) -> None:
    return lambda generator, scene: FadeInScene(
        generator, scene, fade, wait=wait
    )
