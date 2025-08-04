from dataclasses import KW_ONLY, dataclass, field, replace
from typing import Any, Self, override

from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.fade import FadeOut
from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.global_config.global_config import config
from nextrpg.scene.eventful_scene import (
    BackgroundEvent,
    BackgroundEventSentinel,
    RpgEventScene,
)
from nextrpg.scene.scene import Scene


@dataclass_with_instance_init(frozen=True)
class FadeOutScene(RpgEventScene):
    sentinel: BackgroundEventSentinel
    _: KW_ONLY
    wait: bool
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    __: Any = not_constructor_below()
    _fade: FadeOut = instance_init(
        lambda self: FadeOut(
            self.scene.get_background_event(self.sentinel).draw_on_screens,
            self.duration,
        )
    )

    @property
    @override
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return self._fade.draw_on_screens

    @override
    def post_tick(self, time_delta: Millisecond, ticked: Self) -> Scene:
        fade = self._fade.tick(time_delta)
        background_removed = ticked.scene.remove_background_event(self.sentinel)
        if not self.wait:
            background_event = BackgroundFadeOut(fade=fade)
            return background_removed.complete(
                self.generator, background_event=background_event
            )

        if fade.complete:
            return background_removed.complete(self.generator)

        ticking = replace(ticked, scene=background_removed)
        return replace(ticking, _fade=fade)


@dataclass(frozen=True, kw_only=True)
class BackgroundFadeOut(BackgroundEvent):
    fade: FadeOut

    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self.fade.draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, fade=self.fade.tick(time_delta))

    @property
    @override
    def complete(self) -> bool:
        return self.fade.complete


@register_rpg_event
def fade_out(
    sentinel: BackgroundEventSentinel,
    /,
    *,
    wait: bool,
    duration: Millisecond | None = None,
) -> None:
    return lambda generator, scene: FadeOutScene(
        generator,
        scene,
        sentinel,
        wait=wait,
        duration=duration or config().transition.duration,
    )
