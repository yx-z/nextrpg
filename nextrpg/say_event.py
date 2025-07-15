"""
Say event system for NextRPG.

This module provides the dialogue system for NextRPG games, allowing
characters and scenes to display text messages with fade-in/fade-out
effects. It handles text rendering, background pop-ups, and user
interaction for dialogue sequences.

The say event system supports both character-based dialogue (where
text appears near a character) and scene-based dialogue (where text
appears at a specific location or centered on screen). It includes
fade animations and keyboard interaction for advancing dialogue.

Key Features:
    - Character and scene-based dialogue
    - Fade-in and fade-out animations
    - Text pop-up backgrounds
    - Keyboard interaction (confirm key)
    - Configurable text styling and positioning
    - Event-driven dialogue flow

Example:
    ```python
    from nextrpg.say_event import SayEvent
    from nextrpg.character_on_screen import CharacterOnScreen

    # Create a dialogue event
    say_event = SayEvent(
        character_or_scene=character,
        message="Hello, adventurer!",
        generator=event_generator
    )

    # Handle the dialogue
    scene = say_event.event(key_press_event)
    ```
"""

from dataclasses import field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.area import screen
from nextrpg.character_on_screen import CharacterOnScreen
from nextrpg.coordinate import Coordinate
from nextrpg.core import Millisecond, Size
from nextrpg.draw_on_screen import DrawOnScreen, Rectangle
from nextrpg.draw_on_screen import Drawing
from nextrpg.fade_in import FadeIn
from nextrpg.fade_out import FadeOut
from nextrpg.global_config import config
from nextrpg.model import dataclass_with_instance_init, export, instance_init
from nextrpg.npcs import RpgEventScene
from nextrpg.pygame_event import KeyboardKey, KeyPressDown, PygameEvent
from nextrpg.say_event_config import SayEventConfig
from nextrpg.scene import Scene
from nextrpg.text import Text
from nextrpg.text_on_screen import TextOnScreen


@export
@dataclass_with_instance_init
class SayEvent(RpgEventScene):
    """
    Dialogue event scene for displaying text messages.

    This class provides a complete dialogue system with fade animations,
    text rendering, and user interaction. It can display dialogue
    either near a character or at a specific location in the scene.

    The dialogue includes a background pop-up, fade-in/fade-out effects,
    and keyboard interaction for advancing the dialogue. The text is
    rendered with configurable styling and positioning.

    Arguments:
        `character_or_scene`: The character or scene to display dialogue for.
            If a character, dialogue appears near the character. If a scene,
            dialogue appears at a specified location or centered.

        `message`: The text message to display.

        `arg`: Optional coordinate or drawing for positioning dialogue.
            Used when character_or_scene is a Scene.

        `config`: Configuration for the dialogue appearance and behavior.
            Defaults to the global say event configuration.

        `_background_fade_in`: Internal fade-in animation for the background.

        `_fade_out`: Internal flag indicating fade-out state.

        `_pop_up_fade_out`: Internal fade-out animation for the pop-up.

    Example:
        ```python
        from nextrpg.say_event import SayEvent

        # Character dialogue
        say_event = SayEvent(
            character_or_scene=character,
            message="Hello there!",
            generator=event_generator
        )

        # Scene dialogue at specific location
        say_event = SayEvent(
            character_or_scene=scene,
            message="System message",
            arg=Coordinate(100, 100),
            generator=event_generator
        )
        ```
    """

    character_or_scene: CharacterOnScreen | Scene
    message: str
    arg: Coordinate | Drawing | None = None
    config: SayEventConfig = field(default_factory=lambda: config().say_event)
    _background_fade_in: FadeIn = instance_init(
        lambda self: FadeIn(
            resource=self._pop_up,
            duration=self.config.fade_duration,
        )
    )
    _fade_out: bool = False
    _pop_up_fade_out: FadeOut = instance_init(
        lambda self: FadeOut(
            resource=self._pop_up + self._text_on_screen,
            duration=self.config.fade_duration,
        )
    )

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the drawable elements for the dialogue scene.

        Returns different sets of drawables based on the current
        state of the dialogue (fade-in, normal, or fade-out).

        Returns:
            `tuple[DrawOnScreen, ...]`: The drawable elements for the scene.

        Example:
            ```python
            drawables = say_event.draw_on_screens
            for drawable in drawables:
                screen.draw(drawable)
            ```
        """
        if self._fade_out:
            return (
                self.scene.draw_on_screens
                + self._pop_up_fade_out.draw_on_screens
            )
        return (
            self.scene.draw_on_screens
            + self._background_fade_in.draw_on_screens
            + self._text_on_screen
        )

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        """
        Update the dialogue scene for a single game frame.

        Handles fade animations and scene transitions. When the
        fade-out animation completes, the dialogue returns to
        the original scene.

        Arguments:
            `time_delta`: The time elapsed since the last update
                in milliseconds.

        Returns:
            `SayEvent`: The updated dialogue scene state.

        Example:
            ```python
            # Update dialogue in game loop
            say_event = say_event.tick(time_delta)
            ```
        """
        if self._pop_up_fade_out.complete:
            return self.scene.send(self.generator)
        scene = self.scene.tick_without_event(time_delta)
        if self._fade_out:
            return replace(
                self,
                scene=scene,
                _pop_up_fade_out=self._pop_up_fade_out.tick(time_delta),
            )
        return replace(
            self,
            scene=scene,
            _background_fade_in=self._background_fade_in.tick(time_delta),
        )

    @override
    def event(self, e: PygameEvent) -> Scene:
        """
        Handle pygame events for the dialogue scene.

        Processes keyboard input for dialogue advancement.
        The confirm key triggers the fade-out animation to
        close the dialogue.

        Arguments:
            `e`: The pygame event to process.

        Returns:
            `Scene`: The updated scene after event processing.

        Example:
            ```python
            # Handle keyboard input
            scene = say_event.event(key_press_event)
            ```
        """
        if not isinstance(e, KeyPressDown):
            scene = self.scene.event_without_npc_trigger(e)
            return replace(self, scene=scene)

        if e.key is KeyboardKey.CONFIRM:
            return replace(self, _fade_out=True)
        return self

    @cached_property
    def _text_on_screen(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the text drawables for the dialogue.

        Returns the text rendering elements when the background
        fade-in animation has completed.

        Returns:
            `tuple[DrawOnScreen, ...]`: The text drawable elements.

        Example:
            ```python
            text_drawables = say_event._text_on_screen
            ```
        """
        if self._background_fade_in.complete:
            return TextOnScreen(self._text_top_left, self._text).draw_on_screens
        return ()

    @cached_property
    def _pop_up(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the pop-up background elements.

        Returns the background pop-up and any additional
        visual elements for the dialogue.

        Returns:
            `tuple[DrawOnScreen, ...]`: The pop-up background elements.

        Example:
            ```python
            pop_up_elements = say_event._pop_up
            ```
        """
        return (self._background,) + self._text_tail

    @cached_property
    def _text_tail(self) -> tuple[DrawOnScreen, ...]:
        """
        Get additional visual elements for the text.

        Returns any additional drawable elements that should
        be rendered with the text (e.g., borders, decorations).

        Returns:
            `tuple[DrawOnScreen, ...]`: Additional text visual elements.

        Example:
            ```python
            tail_elements = say_event._text_tail
            ```
        """
        return ()

    @cached_property
    def _text(self) -> Text:
        """
        Get the text object for the dialogue message.

        Creates a Text object with the dialogue message and
        configured styling.

        Returns:
            `Text`: The text object for rendering.

        Example:
            ```python
            text_obj = say_event._text
            print(f"Text size: {text_obj.size}")
            ```
        """
        return Text(self.message, self.config.text)

    @cached_property
    def _text_top_left(self) -> Coordinate:
        """
        Get the top-left coordinate for text positioning.

        Calculates the position for the dialogue text based on
        whether it's character-based or scene-based dialogue.

        Returns:
            `Coordinate`: The top-left position for the text.

        Example:
            ```python
            text_pos = say_event._text_top_left
            ```
        """
        if isinstance(self.character_or_scene, Scene):
            return self._scene_top_left

        coord = self.character_or_scene.coordinate
        if self.scene.draw_on_screen_shift:
            return coord.shift(self.scene.draw_on_screen_shift)
        return coord

    @cached_property
    def _scene_top_left(self) -> Coordinate:
        """
        Get the top-left coordinate for scene-based dialogue.

        Calculates the position for dialogue when displayed
        in a scene context, either at a specific coordinate
        or centered on screen.

        Returns:
            `Coordinate`: The top-left position for scene dialogue.

        Example:
            ```python
            scene_pos = say_event._scene_top_left
            ```
        """
        center = (
            self.arg if isinstance(self.arg, Coordinate) else screen().center
        )
        width, height = self._text.size
        return center.shift(Coordinate(width / 2, height / 2).negate)

    @cached_property
    def _background(self) -> DrawOnScreen:
        """
        Get the background pop-up for the dialogue.

        Creates a rectangular background with padding and
        border radius for the dialogue pop-up.

        Returns:
            `DrawOnScreen`: The background pop-up element.

        Example:
            ```python
            background = say_event._background
            ```
        """
        width, height = self._text.size
        top_left = self._text_top_left.shift(
            Coordinate(self.config.padding, self.config.padding).negate
        )
        padding = self.config.padding * 2
        size = Size(width + padding, height + padding)
        return Rectangle(top_left, size).fill(
            self.config.background, self.config.border_radius
        )
