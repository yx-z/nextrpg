from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import override

from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.scene.rpg_event_scene import RpgEventScene
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.model import (
    dataclass_with_instance_init,
    instance_init,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.draw.fade import FadeIn, FadeOut
from nextrpg.draw.typewriter import Typewriter
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class SayEventAddOn(RpgEventScene, ABC):
    npc_object_name: str | None
    initial_coord: Coordinate | None

    @property
    @abstractmethod
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        """"""

    @override
    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if self.npc_object_name:
            npc = self.scene.get_npc(self.npc_object_name)
            diff = npc.coordinate.shift(self.initial_coord.negate)
            add_on = tuple(a.shift(diff) for a in self.add_ons)
        else:
            add_on = self.add_ons

        return self.scene.draw_on_screens + add_on


@dataclass_with_instance_init
class FadeInAddOn(SayEventAddOn):
    background: tuple[DrawOnScreen, ...]
    text: TextOnScreen
    config: SayEventConfig
    fade_in: FadeIn = instance_init(
        lambda self: FadeIn(
            resource=self.background, duration=self.config.fade_duration
        )
    )

    @property
    @override
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return self.fade_in.draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        fade_in = self.fade_in.tick(time_delta)
        scene = self.scene.tick_without_event(time_delta)
        if fade_in.complete:
            return TypingAddOn(
                scene=scene,
                background=self.background,
                text=self.text,
                config=self.config,
                generator=self.generator,
                npc_object_name=self.npc_object_name,
                initial_coord=self.initial_coord,
            )
        return replace(self, scene=scene, fade_in=fade_in)


@dataclass_with_instance_init
class TypingAddOn(SayEventAddOn):
    background: tuple[DrawOnScreen, ...]
    text: TextOnScreen
    config: SayEventConfig
    typewriter: Typewriter | None = instance_init(
        lambda self: (
            Typewriter(text_on_screen=self.text, delay=delay)
            if (delay := self.config.text_delay)
            else None
        )
    )

    @override
    @property
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        text = (
            self.typewriter.draw_on_screens
            if self.typewriter
            else self.text.draw_on_screens
        )
        return self.background + text

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        typewriter = (
            self.typewriter.tick(time_delta) if self.typewriter else None
        )
        scene = self.scene.tick_without_event(time_delta)
        return replace(self, scene=scene, typewriter=typewriter)

    @override
    def event(self, event: PygameEvent) -> Scene:
        if isinstance(event, KeyPressDown) and event.key is KeyboardKey.CONFIRM:
            return FadeOutAddOn(
                scene=self.scene,
                draws=self.background + self.text.draw_on_screens,
                config=self.config,
                generator=self.generator,
                npc_object_name=self.npc_object_name,
                initial_coord=self.initial_coord,
            )
        return self


@dataclass_with_instance_init
class FadeOutAddOn(SayEventAddOn):
    draws: tuple[DrawOnScreen, ...]
    config: SayEventConfig
    fade_out: FadeOut = instance_init(
        lambda self: FadeOut(
            resource=self.draws, duration=self.config.fade_duration
        )
    )

    @override
    @property
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return self.fade_out.draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        fade_out = self.fade_out.tick(time_delta)
        scene = self.scene.tick_without_event(time_delta)
        if fade_out.complete:
            return scene.send(self.generator)
        return replace(self, scene=scene, fade_out=fade_out)
