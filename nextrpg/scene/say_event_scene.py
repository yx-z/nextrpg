"""
Say event system for `NextRPG`.

This module provides the dialogue system for `NextRPG` games, allowing
characters and scenes to display text messages with fade-in/fade-out
effects. It handles text rendering, background pop-ups, and user
interaction for dialogue sequences.

The say event system supports both character-based dialogue (where text
appears near a character) and scene-based dialogue (where text appears at a
specific location or centered on screen). It includes fade animations and
keyboard interaction for advancing dialogue.

Key Features:
    - Character and scene-based dialogue
    - Fade-in and fade-out animations
    - Text pop-up backgrounds
    - Keyboard interaction (confirm key)
    - Configurable text styling and positioning
    - Event-driven dialogue flow
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg import Animated, MovingNpcOnScreen
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npcs import RpgEventScene
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.model import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.color import BLACK
from nextrpg.draw.draw_on_screen import DrawOnScreen, Drawing, Rectangle
from nextrpg.draw.fade import FadeIn, FadeOut
from nextrpg.draw.text import Text
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.draw.typewriter import Typewriter
from nextrpg.event.pygame_event import KeyPressDown, KeyboardKey, PygameEvent
from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.global_config.global_config import config
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.gui.area import screen
from nextrpg.scene.scene import Scene


@register_rpg_event
def say(
    character_or_scene: CharacterOnScreen | Scene,
    message: str,
    arg: Coordinate | Drawing | SayEventConfig | None = None,
) -> None:
    """
    Display a message from a character or scene using a say event.

    This function creates a say event that displays a message from a character
    or scene. It is registered as an RPG event and can be used in event scripts.

    Arguments:
        `character_or_scene`: The character or scene that will say the message.
        `message`: The message to say.
        `arg`: Optional coordinate argument for positioning. Defaults to `None`.
        `**kwargs`: Additional keyword arguments passed to the say event.

    Returns:
        `None`: For user code (`RpgEventSpec`), `say` returns no result (from
        the `SayEvent` scene). For `Npcs`/`MapScene` to yield the scene
        coroutine, it returns an `RpgEventCallable`.
    """
    return lambda generator, scene: SayEventScene(
        generator=generator,
        scene=scene,
        character_or_scene=character_or_scene,
        message=message,
        arg=arg,
    )


@dataclass_with_instance_init
class SayEventScene(RpgEventScene):
    """
    Dialogue event scene for displaying text messages.

    This class provides a complete dialogue system with fade animations, text
    rendering, and user interaction. It can display dialogue either near a
    character or at a specific location in the scene.

    The dialogue includes a background pop-up, fade-in/fade-out effects, and
    keyboard interaction for advancing the dialogue. The text is rendered with
    configurable styling and positioning.

    Arguments:
        `character_or_scene`: The character or scene to display dialogue for.
            If a character, dialogue appears near the character. If a scene,
            dialogue appears at a specified location or centered.
        `message`: The text message to display.
        `arg`: Optional coordinate or drawing for positioning dialogue. Used
            when `character_or_scene` is a `Scene`.
        `global_config`: Configuration for the dialogue appearance and behavior.
            Defaults to the global say event configuration.
        `_background_fade_in`: Internal fade-in animation for the background.
        `_fade_out`: Internal flag indicating fade-out state.
        `_pop_up_fade_out`: Internal fade-out animation for the pop-up.
    """

    character_or_scene: CharacterOnScreen | Scene
    message: str
    arg: Coordinate | Drawing | SayEventConfig | None = None
    _: KW_ONLY = not_constructor_below()
    config: SayEventConfig = instance_init(lambda self: self._init_config)
    _state: Scene = instance_init(lambda self: self._init_state)

    @override
    @property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self._state.draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        return self._state.tick(time_delta)

    @property
    def _init_state(self) -> Scene:
        character_object_name = (
            self.character_or_scene.spec.object_name
            if isinstance(self.character_or_scene, MovingNpcOnScreen)
            else None
        )
        initial_coord = (
            self.scene.get_npc(character_object_name).coordinate
            if character_object_name
            else None
        )
        return _FadeIn(
            scene=self.scene,
            background=self._background,
            text=self._text_on_screen,
            config=self.config,
            generator=self.generator,
            npc_object_name=character_object_name,
            initial_coord=initial_coord,
        )

    @cached_property
    def _init_config(self) -> SayEventConfig:
        match self.arg:
            case SayEventConfig():
                return self.arg
            case None:
                return config().say_event
            case Coordinate():
                return replace(config().say_event, center=self.arg)
            case Drawing():
                return replace(config().say_event, drawing=self.arg)
        raise ValueError(
            f"Expect SayEventConfig | Coordinate | Drawing | None. Got {self.arg}"
        )

    @cached_property
    def _text_on_screen(self) -> TextOnScreen:
        return TextOnScreen(self._text_top_left, self._text)

    @cached_property
    def _background(self) -> tuple[DrawOnScreen, ...]:
        if isinstance(self.character_or_scene, Scene):
            return (self._text_background,)
        # TODO: Implement text tail/tick
        return (self._text_background,)

    @cached_property
    def _text(self) -> Text:
        black_text = replace(config().text, color=BLACK)
        return Text(self.message, self.config.text or black_text)

    @cached_property
    def _text_top_left(self) -> Coordinate:
        if isinstance(self.character_or_scene, Scene):
            return self._scene_top_left

        coord = self.character_or_scene.coordinate
        if self.scene.draw_on_screen_shift:
            return coord.shift(self.scene.draw_on_screen_shift)
        return coord

    @cached_property
    def _scene_top_left(self) -> Coordinate:
        center = self.config.center or screen().center
        width, height = self._text.size
        return center.shift(Coordinate(width / 2, height / 2).negate)

    @cached_property
    def _text_background(self) -> DrawOnScreen:
        width, height = self._text.size
        top_left = self._text_top_left.shift(
            Coordinate(self.config.padding, self.config.padding).negate
        )
        padding = self.config.padding * 2
        size = Size(width + padding, height + padding)
        return Rectangle(top_left, size).fill(
            self.config.background, self.config.border_radius
        )


@dataclass(frozen=True)
class _SayEventAddOn(RpgEventScene, ABC):
    npc_object_name: str | None
    initial_coord: Coordinate | None

    @property
    @abstractmethod
    def add_ons(self) -> tuple[DrawOnScreen, ...]:
        return NotImplemented

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
class _FadeIn(_SayEventAddOn):
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

    def tick(self, time_delta: Millisecond) -> Scene:
        fade_in = self.fade_in.tick(time_delta)
        scene = self.scene.tick_without_event(time_delta)
        if fade_in.complete:
            return _Typing(
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
class _Typing(_SayEventAddOn):
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
        return replace(
            self,
            scene=self.scene.tick_without_event(time_delta),
            typewriter=typewriter,
        )

    @override
    def event(self, event: PygameEvent) -> Scene:
        if isinstance(event, KeyPressDown) and event.key is KeyboardKey.CONFIRM:
            return _FadeOut(
                scene=self.scene,
                draws=self.background + self.text.draw_on_screens,
                config=self.config,
                generator=self.generator,
                npc_object_name=self.npc_object_name,
                initial_coord=self.initial_coord,
            )
        return self


@dataclass_with_instance_init
class _FadeOut(_SayEventAddOn):
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
        if self.fade_out.complete:
            return self.scene.send(self.generator)

        return replace(
            self,
            scene=self.scene.tick_without_event(time_delta),
            fade_out=self.fade_out.tick(time_delta),
        )
