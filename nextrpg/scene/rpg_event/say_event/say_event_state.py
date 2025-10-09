from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.animation.typewriter import Typewriter
from nextrpg.config.say_event_config import SayEventConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import (
    AnimationOnScreenLike,
    tick_optional,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.text_on_screen import TextOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.rpg_event.rpg_event_scene import RpgEventScene
from nextrpg.scene.scene import Scene


@dataclass_with_default(frozen=True, kw_only=True)
class SayEventState(RpgEventScene, ABC):
    unique_name: str | None
    config: SayEventConfig
    _: KW_ONLY = private_init_below()
    initial_coordinate: Coordinate | None = default(
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


@dataclass_with_default(frozen=True, kw_only=True)
class SayEventFadeInState(SayEventState):
    background: AnimationOnScreenLike
    text_on_screen: TextOnScreen
    config: SayEventConfig
    _: KW_ONLY = private_init_below()
    _fade_in: FadeIn = default(
        lambda self: FadeIn(
            resource=self.background, duration=self.config.fade_duration
        )
    )

    @property
    @override
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade_in.drawing_on_screens

    @override
    def _tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        if not (fade_in := self._fade_in.tick(time_delta)).is_complete:
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


@dataclass_with_default(frozen=True, kw_only=True)
class SayEventTypingState(SayEventState):
    background: AnimationOnScreenLike
    text_on_screen: TextOnScreen
    _: KW_ONLY = private_init_below()
    _typewriter: Typewriter | None = default(
        lambda self: (
            Typewriter(self.text_on_screen, delay)
            if (delay := self.config.text_delay)
            else None
        )
    )

    @override
    def event(self, event: IoEvent) -> Scene:
        if (
            not isinstance(event, KeyPressDown)
            or event.key is not KeyboardKey.CONFIRM
        ):
            return self

        resource = (self.background,) + self.text_on_screen.drawing_on_screens
        animation_on_screens = AnimationOnScreens(resource)
        return SayEventFadeOutState(
            generator=self.generator,
            scene=self.scene,
            unique_name=self.unique_name,
            initial_coordinate=self.initial_coordinate,
            animation_on_screen=animation_on_screens,
            config=self.config,
        )

    @override
    @property
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]:
        if self._typewriter:
            text = self._typewriter.drawing_on_screens
        else:
            text = self.text_on_screen.drawing_on_screens
        return self.background.drawing_on_screens + text

    @override
    def _tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        background = self.background.tick(time_delta)
        typewriter = tick_optional(self._typewriter, time_delta)
        return replace(ticked, background=background, _typewriter=typewriter)


@dataclass_with_default(frozen=True, kw_only=True)
class SayEventFadeOutState(SayEventState):
    animation_on_screen: AnimationOnScreenLike
    config: SayEventConfig
    _: KW_ONLY = private_init_below()
    _fade_out: FadeOut = default(
        lambda self: FadeOut(
            resource=self.animation_on_screen,
            duration=self.config.fade_duration,
        )
    )

    @override
    @property
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade_out.drawing_on_screens

    @override
    def _tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        if (fade_out := self._fade_out.tick(time_delta)).is_complete:
            return ticked.scene.is_complete(self.generator)
        return replace(ticked, _fade_out=fade_out)
