"""
Character on-screen representation for NextRPG.

This module provides the base classes for characters that can be
displayed and interacted with on screen. It includes character
specifications, on-screen character management, and event handling
for character interactions.

The module defines the foundational classes for character representation,
including character specifications, on-screen positioning, drawing
management, and event interaction capabilities.

Key Features:
    - Character specification and configuration
    - On-screen character positioning and drawing
    - Event interaction handling
    - Character state management
    - Visual representation management

Example:
    ```python
    from nextrpg.character_on_screen import CharacterOnScreen, CharacterSpec
    from nextrpg.character_drawing import CharacterDrawing
    from nextrpg.coordinate import Coordinate

    # Create a character specification
    spec = CharacterSpec(
        object_name="player",
        display_name="Hero",
        character=CharacterDrawing(drawing=player_sprite)
    )

    # Create an on-screen character
    character = CharacterOnScreen(
        spec=spec,
        coordinate=Coordinate(100, 100)
    )
    ```
"""

from dataclasses import replace
from functools import cached_property
from typing import Self

from nextrpg.character_drawing import CharacterDrawing
from nextrpg.coordinate import Coordinate
from nextrpg.core import Millisecond
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.event_as_attr import EventAsAttr
from nextrpg.model import dataclass_with_instance_init, export, instance_init


@export
@dataclass_with_instance_init
class CharacterSpec:
    """
    Specification for a character's properties and configuration.

    This class defines the basic properties of a character including
    its object name, display name, and character drawing. It serves
    as a template for creating character instances.

    Arguments:
        `object_name`: The unique identifier for the character object.
            Used for map object references and event triggers.

        `display_name`: The name displayed to the player for this character.
            Defaults to the object_name if not specified.

        `character`: The character drawing that defines the visual
            representation and animation of the character.

    Example:
        ```python
        from nextrpg.character_on_screen import CharacterSpec
        from nextrpg.character_drawing import CharacterDrawing

        spec = CharacterSpec(
            object_name="npc_merchant",
            display_name="Shopkeeper",
            character=CharacterDrawing(drawing=merchant_sprite)
        )
        ```
    """

    object_name: str
    display_name: str = instance_init(lambda self: self.object_name)
    character: CharacterDrawing


@export
@dataclass_with_instance_init
class CharacterOnScreen(EventAsAttr):
    """
    Represents a character that can be displayed and interacted with on screen.

    This class provides the foundation for all on-screen characters,
    including positioning, drawing management, event handling, and
    state management. It serves as the base class for both player
    characters and NPCs.

    The character maintains its position, visual representation,
    and event interaction capabilities. It can be updated over time
    and can participate in event-driven interactions with other
    characters or game elements.

    Arguments:
        `spec`: The character specification defining the character's
            properties and visual representation.

        `coordinate`: The current position of the character on screen.

        `name`: The display name of the character. Defaults to the
            specification's display name.

        `character`: The character drawing that defines the visual
            representation. Defaults to the specification's character.

        `_event_triggered`: Internal flag indicating if the character
            is currently participating in an event.

    Example:
        ```python
        from nextrpg.character_on_screen import CharacterOnScreen
        from nextrpg.coordinate import Coordinate

        character = CharacterOnScreen(
            spec=character_spec,
            coordinate=Coordinate(100, 100)
        )

        # Update character state
        character = character.tick(time_delta)
        ```
    """

    spec: CharacterSpec
    coordinate: Coordinate
    name: str = instance_init(lambda self: self.spec.display_name)
    character: CharacterDrawing = instance_init(
        lambda self: self.spec.character
    )
    _event_triggered: bool = False

    @cached_property
    def character_and_visuals(self) -> tuple[DrawOnScreen, ...]:
        """
        Get all visual elements associated with this character.

        Returns the character's main drawing and any additional
        visual elements that should be rendered with the character.

        Returns:
            `tuple[DrawOnScreen, ...]`: All visual elements for the character.

        Example:
            ```python
            visuals = character.character_and_visuals
            for visual in visuals:
                screen.draw(visual)
            ```
        """
        return (self.draw_on_screen,)

    @cached_property
    def draw_on_screen(self) -> DrawOnScreen:
        """
        Get the character's main drawing representation.

        Creates a drawable representation of the character at its
        current position with its current visual state.

        Returns:
            `DrawOnScreen`: The character's drawing at its current position.

        Example:
            ```python
            drawing = character.draw_on_screen
            screen.draw(drawing)
            ```
        """
        return DrawOnScreen(self.coordinate, self.character.drawing)

    def tick(self, time_delta: Millisecond) -> Self:
        """
        Update the character's state for a single game loop iteration.

        Updates the character's animation and internal state based
        on the elapsed time. This is called each frame to keep
        the character's visual state current.

        Arguments:
            `time_delta`: The elapsed time since the last update
                in milliseconds.

        Returns:
            `CharacterOnScreen`: The updated character state after the tick.

        Example:
            ```python
            # Update character in game loop
            character = character.tick(time_delta)
            ```
        """
        return replace(self, character=self.character.tick_idle(time_delta))

    def start_event(self, character: CharacterOnScreen) -> Self:
        """
        Start an event interaction with another character.

        When starting an event, the character turns to face the
        other character and enters an event-triggered state.
        This ensures proper positioning for dialogue or interactions.

        Arguments:
            `character`: The character to start an event with.

        Returns:
            `CharacterOnScreen`: The updated character state for the event.

        Example:
            ```python
            # Start interaction
            character = character.start_event(other_character)
            ```
        """
        direction = character.coordinate.relative_to(self.coordinate)
        turned_character = self.character.turn(direction)
        return replace(self, character=turned_character, _event_triggered=True)

    @cached_property
    def complete_event(self) -> Self:
        """
        Complete the current event and return to normal state.

        Resets the event-triggered flag and returns the character
        to its normal interaction state.

        Returns:
            `CharacterOnScreen`: The character state after completing the event.

        Example:
            ```python
            # Complete event interaction
            character = character.complete_event
            ```
        """
        return replace(self, _event_triggered=False)

    def _visuals(self, visuals: tuple) -> tuple[DrawOnScreen, ...]:
        """
        Get additional visual elements for the character.

        Processes a list of visual functions and returns their
        drawable representations.

        Arguments:
            `visuals`: Tuple of visual functions to process.

        Returns:
            `tuple[DrawOnScreen, ...]`: Additional visual elements.

        Example:
            ```python
            extra_visuals = character._visuals(visual_functions)
            ```
        """
        return tuple(d for f in visuals for d in f(self))
