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

from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import override

from nextrpg import (
    TextConfig,
    bottom_left_screen,
    top_left_screen,
    top_right_screen,
)
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.moving_npc_on_screen import MovingNpcOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import Drawing, DrawOnScreen, Rectangle
from nextrpg.draw.text import Text
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.global_config.global_config import config
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.gui.area import screen
from nextrpg.scene.rpg_event_scene import RpgEventScene
from nextrpg.scene.say_event_scene_add_on import FadeInAddOn
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
        return FadeInAddOn(
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
    def _name_on_screen(self) -> TextOnScreen | None:
        if not self._name:
            return None
        left, top = self._text_top_left
        coord = Coordinate(
            left, top - self._name.size.height - self.config.padding
        )
        return TextOnScreen(coord, self._name)

    @cached_property
    def _text_on_screen(self) -> TextOnScreen:
        return TextOnScreen(self._text_top_left, self._text)

    @cached_property
    def _background(self) -> tuple[DrawOnScreen, ...]:
        if isinstance(self.character_or_scene, Scene):
            return (self._text_background,)
        # TODO: Implement text tail/tick
        res = (self._text_background,)
        if self._name_on_screen:
            return res + self._name_on_screen.draw_on_screens
        return res

    @cached_property
    def _name(self) -> Text | None:
        if isinstance(self.character_or_scene, Scene):
            return None
        if not self.config.name_color:
            return None
        text_config = replace(self._text_config, color=self.config.name_color)
        return Text(self.character_or_scene.display_name, text_config)

    @cached_property
    def _text_config(self) -> TextConfig:
        return (
            self.config.default_text_config or self.config.default_text_config
        )

    @cached_property
    def _text(self) -> Text:
        return Text(self.message, self._text_config)

    @cached_property
    def _text_top_left(self) -> Coordinate:
        if isinstance(self.character_or_scene, Scene):
            return self._scene_top_left

        if self.scene.draw_on_screen_shift:
            top_left = (
                self.character_or_scene.coordinate
                + self.scene.draw_on_screen_shift
            )
        else:
            top_left = self.character_or_scene.coordinate

        rect = self.character_or_scene.draw_on_screen.rectangle
        shift = self.config.pop_up_shift
        print(f"{top_left=} {top_right_screen()=}")
        if top_left_screen().contain(top_left):
            coord = rect.bottom_center + shift
        elif top_right_screen().contain(top_left):
            coord = rect.bottom_center + shift.negate_left
        elif bottom_left_screen().contain(top_left):
            coord = rect.top_center + shift.negate_top
        else:
            coord = rect.top_center - shift

        centered_coord = coord - self._text.size.all_dimension_scale(0.5)
        if self.scene.draw_on_screen_shift:
            centered_coord = centered_coord + self.scene.draw_on_screen_shift

        if self._name:
            name_height = self._name.size.height + self.config.padding
            width, height = centered_coord
            return Coordinate(width, height + name_height)
        return centered_coord

    @cached_property
    def _scene_top_left(self) -> Coordinate:
        center = self.config.center or screen().center
        return center - self._text.size.all_dimension_scale(0.5)

    @cached_property
    def _text_background(self) -> DrawOnScreen:
        if self._name:
            name_width, name_height = self._name.size
        else:
            name_width = 0
            name_height = 0

        left, top = self._text_top_left
        padding = self.config.padding
        top_left = Coordinate(left - padding, top - 2 * padding - name_height)

        width, height = self._text.size
        background_width = max(width, name_width) + 2 * padding
        background_height = height + 3 * padding + name_height
        size = Size(background_width, background_height)

        return Rectangle(top_left, size).fill(
            self.config.background, self.config.border_radius
        )
