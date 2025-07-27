from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import override

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.fade import FadeIn, FadeOut
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.draw.typewriter import Typewriter
from nextrpg.event.pygame_event import KeyboardKey, KeyPressDown, PygameEvent
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.scene.rpg_event_scene import RpgEventScene
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class SayEventState(RpgEventScene, ABC):
    character_object_name: str | None
    initial_coord: Coordinate | None

    @property
    @abstractmethod
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        """"""

    @override
    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if self.character_object_name:
            character = self.scene.get_character(self.character_object_name)
            diff = character.coordinate - self.initial_coord
            add_on = tuple(a + diff for a in self.add_ons)
        else:
            add_on = self.add_ons

        return self.scene.draw_on_screens + add_on


@dataclass_with_instance_init(frozen=True)
class FadeInState(SayEventState):
    background: tuple[DrawOnScreen, ...]
    text_on_screen: TextOnScreen
    config: SayEventConfig
    fade_in: FadeIn = instance_init(
        lambda self: FadeIn(self.background, self.config.fade_duration)
    )

    @property
    @override
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return self.fade_in.draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        fade_in = self.fade_in.tick(time_delta)
        scene = self.scene.tick_without_event(time_delta)
        if not fade_in.complete:
            return replace(self, scene=scene, fade_in=fade_in)
        return TypingState(
            self.generator,
            scene,
            self.character_object_name,
            self.initial_coord,
            self.background,
            self.text_on_screen,
            self.config,
        )


@dataclass_with_instance_init(frozen=True)
class TypingState(SayEventState):
    background: tuple[DrawOnScreen, ...]
    text_on_screen: TextOnScreen
    config: SayEventConfig
    typewriter: Typewriter | None = instance_init(
        lambda self: (
            Typewriter(self.text_on_screen, delay)
            if (delay := self.config.text_delay)
            else None
        )
    )

    @override
    @property
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        if self.typewriter:
            text = self.typewriter.draw_on_screens
        else:
            text = self.text_on_screen.draw_on_screens
        return self.background + text

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        if self.typewriter:
            typewriter = self.typewriter.tick(time_delta)
        else:
            typewriter = None

        scene = self.scene.tick_without_event(time_delta)
        return replace(self, scene=scene, typewriter=typewriter)

    @override
    def event(self, event: PygameEvent) -> Scene:
        if (
            not isinstance(event, KeyPressDown)
            or event.key is not KeyboardKey.CONFIRM
        ):
            return self
        return FadeOutState(
            self.generator,
            self.scene,
            self.character_object_name,
            self.initial_coord,
            self.background + self.text_on_screen.draw_on_screens,
            self.config,
        )


@dataclass_with_instance_init(frozen=True)
class FadeOutState(SayEventState):
    draws: tuple[DrawOnScreen, ...]
    config: SayEventConfig
    fade_out: FadeOut = instance_init(
        lambda self: FadeOut(self.draws, self.config.fade_duration)
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
