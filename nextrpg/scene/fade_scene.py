from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.fade import FadeIn
from nextrpg.scene.rpg_event_scene import RpgEventScene


@dataclass(frozen=True)
class FadeInScene(RpgEventScene):
    fade: FadeIn
    wait: bool = True

    @override
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return self.fade.draw_on_screens

    @override
    def post_tick(self, time_delta: Millisecond, ticked: Self) -> Self:
        if not self.wait:
            ...
        fade = self.fade.tick(time_delta)
        return replace(ticked, fade=fade)
