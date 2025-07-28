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
from nextrpg.draw.draw import Draw, DrawOnScreen, RectangleDraw
from nextrpg.draw.group import DrawRelativeTo, Group
from nextrpg.draw.text import Text
from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.global_config.global_config import config
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.global_config.text_config import TextConfig
from nextrpg.scene.rpg_event_scene import RpgEventScene
from nextrpg.scene.say_event.add_on import CharacterAddOn, SceneAddOn
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
    @cached_property
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
    def _character_add_on(self) -> CharacterAddOn | None:
        if isinstance(c := self.character_or_scene, CharacterOnScreen):
            name = c.spec.object_name
            ticked_character = self.scene.get_character(name)
            return CharacterAddOn(
                self._text,
                self._add_on,
                self._background,
                self.config,
                self.scene,
                ticked_character,
            )
        return None

    @cached_property
    def _scene_add_on(self) -> SceneAddOn | None:
        if isinstance(self.character_or_scene, Scene):
            return SceneAddOn(
                self._text, self._add_on, self._background, self.config
            )
        return None

    @cached_property
    def _state(self) -> FadeInState:
        if isinstance(self.character_or_scene, CharacterOnScreen):
            object_name = self.character_or_scene.spec.object_name
            text_on_screen = self._character_add_on.text_on_screen
            background = self._character_add_on.background
        else:
            object_name = None
            text_on_screen = self._scene_add_on.text_on_screen
            background = self._scene_add_on.background

        return FadeInState(
            generator=self.generator,
            scene=self.scene,
            object_name=object_name,
            background=background,
            text_on_screen=text_on_screen,
            config=self.config,
        )

    @cached_property
    def _add_on(self) -> Group:
        leader = self._text.group
        followers = tuple(d for d in (self._avatar, self._name) if d)
        content = Group(leader, followers)
        background, shift = self._background
        return Group(background, DrawRelativeTo(content, shift))

    @cached_property
    def _background(self) -> DrawRelativeTo:
        padding = self.config.padding
        text_width, text_height = self._text.size
        relative_to_width = padding
        relative_to_height = padding

        rect_height = text_height + 2 * padding
        if self._name:
            extra_height = self._name.draw.size.height + padding
            relative_to_height += extra_height
            rect_height += extra_height

        rect_width = text_width + 2 * padding
        if self._avatar:
            extra_width = self._avatar.draw.size.width + padding
            relative_to_width += extra_width
            rect_width += extra_width

        size = Size(rect_width, rect_height)
        rect = RectangleDraw(
            size, self.config.background, self.config.border_radius
        )
        shift = Size(relative_to_width, relative_to_height)
        return DrawRelativeTo(rect, shift)

    @cached_property
    def _avatar(self) -> DrawRelativeTo | None:
        if not (avatar := self.config.avatar):
            return None
        width, height = avatar.size
        left_shift = -self.config.padding - width
        top_shift = self._text.size.height - height
        shift = Size(left_shift, top_shift)
        return DrawRelativeTo(avatar, shift)

    @cached_property
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
        return DrawRelativeTo(text.group, shift)

    @cached_property
    def _text(self) -> Text:
        return Text(self.message, self._text_config)

    @cached_property
    def _text_config(self) -> TextConfig:
        return self.config.text or self.config.default_text_config


def _update_config(cfg: SayEventArg, arg: SayEventArg) -> SayEventConfig:
    match arg:
        case SayEventConfig():
            return arg
        case Coordinate():
            return replace(cfg, coordinate=arg)
        case Draw():
            return replace(cfg, avatar=arg)
        case str():
            return replace(cfg, name_override=arg)
    raise ValueError(
        f"Expect str | Coordinate | Draw | SayEventConfig. Got {arg}"
    )
