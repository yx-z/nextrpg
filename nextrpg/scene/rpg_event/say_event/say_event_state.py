from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.animation.typewriter import Typewriter
from nextrpg.config.say_event_config import SayEventConfig
from nextrpg.core.dataclass_with_default_init import (
    dataclass_with_default_init,
    default_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.event.pygame_event import KeyboardKey, KeyPressDown, PygameEvent
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.rpg_event.rpg_event_scene import RpgEventScene
from nextrpg.scene.scene import Scene


@dataclass_with_default_init(frozen=True, kw_only=True)
class SayEventState(RpgEventScene, ABC):
    unique_name: str | None
    config: SayEventConfig
    _: KW_ONLY = not_constructor_below()
    initial_coordinate: Coordinate | None = default_init(
        lambda self: (
            self.scene.get_character(n).coordinate
            if (n := self.unique_name)
            else None
        )
    )

    @override
    @cached_property
    def add_ons(self) -> tuple[DrawingOnScreen, ...]:
        if self.unique_name:
            character = self.scene.get_character(self.unique_name)
            diff = character.coordinate - self.initial_coordinate
            return tuple(a + diff for a in self._add_ons)
        return self._add_ons

    @property
    @abstractmethod
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]: ...


@dataclass_with_default_init(frozen=True, kw_only=True)
class SayEventFadeInState(SayEventState):
    background: tuple[DrawingOnScreen, ...]
    text_on_screen: TextOnScreen
    config: SayEventConfig
    _: KW_ONLY = not_constructor_below()
    _fade_in: FadeIn = default_init(
        lambda self: FadeIn(self.background, self.config.fade_duration)
    )

    @property
    @override
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade_in.drawing_on_screens

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


@dataclass_with_default_init(frozen=True, kw_only=True)
class SayEventTypingState(SayEventState):
    background: tuple[DrawingOnScreen, ...]
    text_on_screen: TextOnScreen
    _: KW_ONLY = not_constructor_below()
    _typewriter: Typewriter | None = default_init(
        lambda self: (
            Typewriter(self.text_on_screen, delay)
            if (delay := self.config.text_delay)
            else None
        )
    )

    @override
    @property
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]:
        if self._typewriter:
            text = self._typewriter.drawing_on_screens
        else:
            text = self.text_on_screen.drawing_on_screens
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
        drawing_on_screens = (
            self.background + self.text_on_screen.drawing_on_screens
        )
        return SayEventFadeOutState(
            generator=self.generator,
            scene=self.scene,
            unique_name=self.unique_name,
            initial_coordinate=self.initial_coordinate,
            drawing_on_screens_input=drawing_on_screens,
            config=self.config,
        )


@dataclass_with_default_init(frozen=True, kw_only=True)
class SayEventFadeOutState(SayEventState):
    drawing_on_screens_input: tuple[DrawingOnScreen, ...]
    config: SayEventConfig
    _: KW_ONLY = not_constructor_below()
    _fade_out: FadeOut = default_init(
        lambda self: FadeOut(
            self.drawing_on_screens_input, self.config.fade_duration
        )
    )

    @override
    @property
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade_out.drawing_on_screens

    @override
    def tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        fade_out = self._fade_out.tick(time_delta)
        if fade_out.complete:
            return ticked.scene.complete(self.generator)
        return replace(ticked, _fade_out=fade_out)
