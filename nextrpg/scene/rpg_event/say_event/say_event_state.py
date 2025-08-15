from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import DrawOnScreen
from nextrpg.draw.fade import FadeIn, FadeOut
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.draw.typewriter import Typewriter
from nextrpg.event.pygame_event import KeyboardKey, KeyPressDown, PygameEvent
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.scene.rpg_event.eventful_scene import RpgEventScene
from nextrpg.scene.scene import Scene


@dataclass_with_init(frozen=True, kw_only=True)
class SayEventState(RpgEventScene, ABC):
    unique_name: str | None
    config: SayEventConfig
    _: KW_ONLY = not_constructor_below()
    initial_coordinate: Coordinate | None = default(
        lambda self: (
            self.scene.get_character(n).coordinate
            if (n := self.unique_name)
            else None
        )
    )

    @override
    @cached_property
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        if self.unique_name:
            character = self.scene.get_character(self.unique_name)
            diff = character.coordinate - self.initial_coordinate
            return tuple(a + diff for a in self._add_ons)
        return self._add_ons

    @property
    @abstractmethod
    def _add_ons(self) -> tuple[DrawOnScreen, ...]: ...


@dataclass_with_init(frozen=True, kw_only=True)
class SayEventFadeInState(SayEventState):
    background: tuple[DrawOnScreen, ...]
    text_on_screen: TextOnScreen
    config: SayEventConfig
    _: KW_ONLY = not_constructor_below()
    _fade_in: FadeIn = default(
        lambda self: FadeIn(self.background, self.config.fade_duration)
    )

    @property
    @override
    def _add_ons(self) -> tuple[DrawOnScreen, ...]:
        return self._fade_in.draw_on_screens

    @override
    def tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        fade_in = self._fade_in.tick(time_delta)
        if not fade_in.complete:
            return replace(ticked, _fade_in=fade_in)
        return SayEventTypingState(
            generator=self.generator,
            scene=ticked.scene,
            unique_name=self.unique_name,
            initial_coordinate=self.initial_coordinate,
            background=self.background,
            text_on_screen=self.text_on_screen,
            config=self.config,
        )


@dataclass_with_init(frozen=True, kw_only=True)
class SayEventTypingState(SayEventState):
    background: tuple[DrawOnScreen, ...]
    text_on_screen: TextOnScreen
    _: KW_ONLY = not_constructor_below()
    _typewriter: Typewriter | None = default(
        lambda self: (
            Typewriter(self.text_on_screen, delay)
            if (delay := self.config.text_delay)
            else None
        )
    )

    @override
    @property
    def _add_ons(self) -> tuple[DrawOnScreen, ...]:
        if self._typewriter:
            text = self._typewriter.draw_on_screens
        else:
            text = self.text_on_screen.draw_on_screens
        return self.background + text

    @override
    def tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        if self._typewriter:
            typewriter = self._typewriter.tick(time_delta)
        else:
            typewriter = None

        return replace(ticked, _typewriter=typewriter)

    @override
    def event(self, event: PygameEvent) -> Scene:
        if (
            not isinstance(event, KeyPressDown)
            or event.key is not KeyboardKey.CONFIRM
        ):
            return self
        return SayEventFadeOutState(
            generator=self.generator,
            scene=self.scene,
            unique_name=self.unique_name,
            initial_coordinate=self.initial_coordinate,
            draws=self.background + self.text_on_screen.draw_on_screens,
            config=self.config,
        )


@dataclass_with_init(frozen=True, kw_only=True)
class SayEventFadeOutState(SayEventState):
    draws: tuple[DrawOnScreen, ...]
    config: SayEventConfig
    _: KW_ONLY = not_constructor_below()
    _fade_out: FadeOut = default(
        lambda self: FadeOut(self.draws, self.config.fade_duration)
    )

    @override
    @property
    def _add_ons(self) -> tuple[DrawOnScreen, ...]:
        return self._fade_out.draw_on_screens

    @override
    def tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        fade_out = self._fade_out.tick(time_delta)
        if fade_out.complete:
            return ticked.scene.complete(self.generator)
        return replace(ticked, _fade_out=fade_out)
