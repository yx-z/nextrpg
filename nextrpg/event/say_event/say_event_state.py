from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.animation.typewriter import Typewriter
from nextrpg.config.rpg_event.say_event_config import SayEventConfig
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite import tick_optional
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
    animate,
)
from nextrpg.drawing.text_on_screen import TextOnScreen
from nextrpg.event.io_event import IoEvent, is_key_press
from nextrpg.event.rpg_event_scene import RpgEventScene
from nextrpg.game.game_state import GameState
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene


@dataclass_with_default(frozen=True, kw_only=True)
class SayEventState(RpgEventScene, ABC):
    unique_name: str | None
    config: SayEventConfig
    _: KW_ONLY = private_init_below()
    initial_coordinate: Coordinate | None = default(
        lambda self: (
            self.parent.get_character(name).coordinate
            if (name := self.unique_name)
            else None
        )
    )

    @override
    @cached_property
    def drawing_on_screens_after_parent(self) -> tuple[DrawingOnScreen, ...]:
        if self.unique_name:
            character = self.parent.get_character(self.unique_name)
            diff = character.coordinate - self.initial_coordinate
            return tuple(a + diff for a in self._add_ons)
        return self._add_ons

    @property
    @abstractmethod
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]: ...


@dataclass_with_default(frozen=True, kw_only=True)
class SayEventFadeInState(SayEventState):
    background: SpriteOnScreen
    text_on_screen: TextOnScreen
    _: KW_ONLY = private_init_below()
    _fade_in: TimedAnimationOnScreens = default(
        lambda self: animate(
            self.background, FadeIn, duration=self.config.fade_duration
        )
    )

    @override
    @cached_property
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade_in.drawing_on_screens

    @override
    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self, state: GameState
    ) -> tuple[Scene, GameState]:
        if (fade_in := self._fade_in.tick(time_delta)).is_complete:
            scene = SayEventTypingState(
                parent=ticked.parent,
                unique_name=self.unique_name,
                initial_coordinate=self.initial_coordinate,
                background=self.background,
                text_on_screen=self.text_on_screen,
                config=self.config,
            )
        else:
            scene = replace(ticked, _fade_in=fade_in)
        return scene, state


@dataclass_with_default(frozen=True, kw_only=True)
class SayEventTypingState(SayEventState):
    background: SpriteOnScreen
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
    def event(
        self, event: IoEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        if not is_key_press(event, KeyMappingConfig.confirm):
            return self, state

        resource = (self.background,) + self.text_on_screen.drawing_on_screens
        resources = AnimationOnScreens(resource)
        scene = SayEventFadeOutState(
            parent=self.parent,
            unique_name=self.unique_name,
            initial_coordinate=self.initial_coordinate,
            resources=resources,
            config=self.config,
        )
        return scene, state

    @override
    @cached_property
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]:
        if self._typewriter:
            text = self._typewriter.drawing_on_screens
        else:
            text = self.text_on_screen.drawing_on_screens
        return self.background.drawing_on_screens + text

    @override
    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self, state: GameState
    ) -> tuple[Scene, GameState]:
        background = self.background.tick(time_delta)
        typewriter = tick_optional(self._typewriter, time_delta)
        scene = replace(ticked, background=background, _typewriter=typewriter)
        return scene, state


@dataclass_with_default(frozen=True, kw_only=True)
class SayEventFadeOutState(SayEventState):
    resources: SpriteOnScreen
    _: KW_ONLY = private_init_below()
    _fade_out: TimedAnimationOnScreens = default(
        lambda self: animate(
            self.resources, FadeOut, duration=self.config.fade_duration
        )
    )

    @override
    @cached_property
    def _add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return self._fade_out.drawing_on_screens

    @override
    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self, state: GameState
    ) -> tuple[Scene, GameState]:
        if (fade_out := self._fade_out.tick(time_delta)).is_complete:
            scene = ticked.parent.complete()
        else:
            scene = replace(ticked, _fade_out=fade_out)
        return scene, state
