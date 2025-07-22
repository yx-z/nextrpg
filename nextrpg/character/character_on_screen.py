"""
Character on-screen representation for `nextrpg`.

This module provides the base classes for characters that can be displayed and
interacted with on screen. It includes character specifications, on-screen
character management, and event handling for character interactions.

Features:
    - Character specification and configuration
    - On-screen character positioning and drawing
    - Event interaction handling
    - Character state management
    - Visual representation management
"""

from dataclasses import KW_ONLY, replace
from typing import Self, override

from nextrpg.draw.animated_on_screen import AnimatedOnScreen
from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.event_as_attr import event_as_attr
from nextrpg.core.model import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen


@dataclass_with_instance_init
class CharacterSpec:
    """
    Specification for a character's properties and configuration.

    This class defines the basic properties of a character including its object
    name, display name, and character drawing. It serves as a template for
    creating character instances.

    Arguments:
        object_name: The unique identifier for the character object. Used for
            map object references and event triggers.
        display_name: The name displayed to the player for this character.
            Defaults to the object_name if not specified.
        character: The character drawing that defines the visual representation
            and animation of the character.
    """

    object_name: str
    character: CharacterDrawing
    display_name: str = instance_init(lambda self: self.object_name)


@dataclass_with_instance_init
@event_as_attr
class CharacterOnScreen(AnimatedOnScreen):
    """
    Represents a character that can be displayed and interacted with on screen.

    This class provides the foundation for all on-screen characters, including
    positioning, drawing management, event handling, and state management. It
    serves as the base class for both player characters and NPCs.

    The character maintains its position, visual representation, and event
    interaction capabilities. It can be updated over time and can participate
    in event-driven interactions with other characters or game elements.

    Arguments:
        spec: The character specification defining the character's properties
            and visual representation.
        coordinate: The current position of the character on screen.
        name: The display name of the character. Defaults to the specification's
            display name.
        character: The character drawing that defines the visual representation.
            Defaults to the specification's character.
        _event_triggered: Internal flag indicating if the character is currently
            participating in an event.
    """

    spec: CharacterSpec
    coordinate: Coordinate
    _: KW_ONLY = not_constructor_below()
    character: CharacterDrawing = instance_init(
        lambda self: self.spec.character
    )
    _event_triggered: bool = False

    @property
    def display_name(self) -> str:
        return self.spec.display_name

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, character=self.character.tick_idle(time_delta))

    @property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        # TODO: Add visuals.
        return (self.draw_on_screen,)

    @property
    def draw_on_screen(self) -> DrawOnScreen:
        """
        Get the character's main drawing representation.

        Creates a drawable representation of the character at its current
        position with its current visual state.

        Returns:
            The character's drawing at its current position.
        """
        return DrawOnScreen(self.coordinate, self.character.drawing)

    def start_event(self, character: CharacterOnScreen) -> Self:
        """
        Start an event interaction with another character.

        When starting an event, the character turns to face the other character
        and enters an event-triggered state. This ensures proper positioning
        for dialogue or interactions.

        Arguments:
            character: The character to start an event with.

        Returns:
            The updated character state for the event.
        """
        direction = character.coordinate.relative_to(self.coordinate)
        turned_character = self.character.turn(direction)
        return replace(self, character=turned_character, _event_triggered=True)

    @property
    def complete_event(self) -> Self:
        """
        Complete the current event and return to normal state.

        Resets the event-triggered flag and returns the character to its normal
        interaction state.

        Returns:
            The character state after completing the event.
        """
        return replace(self, _event_triggered=False)
