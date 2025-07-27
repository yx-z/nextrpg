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

from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import Draw, DrawOnScreen
from nextrpg.draw.drawing_group import DrawRelativeTo, DrawingGroup
from nextrpg.draw.text import Text
from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.global_config.global_config import config
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.global_config.text_config import TextConfig
from nextrpg.scene.rpg_event_scene import RpgEventScene
from nextrpg.scene.say_event.add_on import CharacterSay, SceneSay
from nextrpg.scene.say_event.state import FadeInState
from nextrpg.scene.scene import Scene

type SayEventArg = str | Coordinate | Size | Draw | SayEventConfig


@register_rpg_event
def say(
    character_or_scene: CharacterOnScreen | Scene,
    message: str,
    *args: SayEventArg,
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
        generator, scene, character_or_scene, message, args
    )


@dataclass(frozen=True)
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
    args: tuple[SayEventArg, ...] = field(default_factory=tuple)

    @override
    @property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self._state.draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        return self._state.tick(time_delta)

    @cached_property
    def config(self) -> SayEventConfig:
        cfg = config().say_event
        for arg in self.args:
            cfg = _update_config(cfg, arg)
        return cfg

    @cached_property
    def _character_say(self) -> CharacterSay | None:
        if isinstance(self.character_or_scene, CharacterOnScreen):
            return CharacterSay(
                self._text,
                self._add_on,
                self.scene,
                self.character_or_scene,
                self.config,
            )
        return None

    @cached_property
    def _scene_say(self) -> SceneSay | None:
        if isinstance(self.character_or_scene, Scene):
            return SceneSay(self._text, self._add_on, self.config)
        return None

    @cached_property
    def _state(self) -> FadeInState:
        if isinstance(self.character_or_scene, CharacterOnScreen):
            character_object_name = self.character_or_scene.spec.object_name
            initial_coord = self.scene.get_character(character_object_name).coordinate
            text_on_screen = self._character_say.text_on_screen
            background = self._character_say.background
        else:
            character_object_name = None
            initial_coord = None
            text_on_screen = self._scene_say.text_on_screen
            background = self._scene_say.background

        return FadeInState(
            self.generator,
            self.scene,
            character_object_name,
            initial_coord,
            background,
            text_on_screen,
            self.config,
        )

    @property
    def _add_on(self) -> DrawingGroup:
        followers = tuple(d for d in (self._drawing, self._name) if d)
        return DrawingGroup(self._text.drawing_group, followers)

    @property
    def _drawing(self) -> DrawRelativeTo | None:
        if not (drawing := self.config.drawing):
            return None
        width, height = drawing.size
        left_shift = -self.config.padding - width
        top_shift = self._text.size.height - height
        shift = Size(left_shift, top_shift)
        return DrawRelativeTo(drawing, shift)

    @property
    def _name(self) -> DrawRelativeTo | None:
        if self.config.name_override:
            name = self.config.name_override
        elif isinstance(self.character_or_scene, CharacterOnScreen):
            name = self.character_or_scene.display_name
        else:
            return None

        text_config = replace(self._text_config, color=self.config.name_color)
        text = Text(name, text_config)

        name_height = text.size.height
        shift = Size(0, -name_height - self.config.padding)
        return DrawRelativeTo(text.drawing_group, shift)

    @cached_property
    def _text(self) -> Text:
        return Text(self.message, self._text_config)

    @property
    def _text_config(self) -> TextConfig:
        return self.config.text or self.config.default_text_config


def _update_config(cfg: SayEventArg, arg: SayEventArg) -> SayEventConfig:
    match arg:
        case SayEventConfig():
            return arg
        case Coordinate():
            return replace(cfg, coordinate=arg)
        case Draw():
            return replace(cfg, drawing=arg)
        case str():
            return replace(cfg, name_override=arg)
    raise ValueError(
        f"Expect str | Coordinate | Draw | SayEventConfig. Got {arg}"
    )
