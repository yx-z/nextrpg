from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg import DrawOnScreen, Millisecond
from nextrpg.character.npc_on_screen import NpcEventGenerator
from nextrpg.scene.eventful_scene import EventfulScene
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class RpgEventScene(Scene):
    generator: NpcEventGenerator
    scene: EventfulScene

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self.scene.draw_on_screens + self.add_ons

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        ticked = replace(self, scene=self.scene.tick_without_event(time_delta))
        return self.post_tick(time_delta, ticked)

    def post_tick(self, time_delta: Millisecond, ticked: Self) -> Self:
        return ticked

    @property
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return ()
