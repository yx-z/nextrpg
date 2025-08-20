from dataclasses import KW_ONLY, dataclass, replace
from typing import Self, override

from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.fade import FadeOut
from nextrpg.event.background_event import (
    BackgroundEvent,
    BackgroundEventSentinel,
)
from nextrpg.scene.rpg_event.rpg_event_scene import (
    RpgEventScene,
    register_rpg_event_scene,
)
from nextrpg.scene.scene import Scene


@dataclass_with_init(frozen=True)
class FadeOutScene(RpgEventScene):
    sentinel: BackgroundEventSentinel
    wait: bool = True
    duration: Millisecond | None = None
    _: KW_ONLY = not_constructor_below()
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
            background_event = BackgroundFadeOut(fade=fade)
            return background_removed.complete(
                self.generator, background_event=background_event
            )

        if fade.complete:
            return background_removed.complete(self.generator)

        ticking = replace(ticked, scene=background_removed)
        return replace(ticking, _fade=fade)

    @property
    def _init_fade(self) -> FadeOut:
        res = self.scene.get_background_event(self.sentinel).draw_on_screens
        if self.duration is None:
            return FadeOut(res)
        return FadeOut(res, self.duration)


@dataclass(frozen=True, kw_only=True)
class BackgroundFadeOut(BackgroundEvent):
    fade: FadeOut

    @override
    def draw_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.fade.drawing_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, fade=self.fade.tick(time_delta))

    @property
    @override
    def complete(self) -> bool:
        return self.fade.complete


@register_rpg_event_scene(FadeOutScene)
def fade_out(
    sentinel: BackgroundEventSentinel,
    wait: bool = True,
    duration: Millisecond | None = None,
) -> None: ...
