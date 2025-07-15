"""
Character drawing interface and base classes for NextRPG.

This module provides the foundational interface for character drawing
and animation in NextRPG games. It defines the abstract base class
`CharacterDrawing` that all character drawing implementations must
inherit from.

The module establishes the contract for character rendering, including:
- Direction-based character orientation
- Movement animation updates
- Idle animation updates
- Drawing state management

This interface ensures consistency across different character drawing
implementations while allowing for specialized rendering techniques.

Example:
    ```python
    from nextrpg.character_drawing import CharacterDrawing
    from nextrpg.core import Direction, Millisecond

    class MyCharacterDrawing(CharacterDrawing):
        def drawing(self):
            # Return the character's drawing
            pass

        def turn(self, direction: Direction):
            # Handle direction changes
            pass

        def tick_move(self, time_delta: Millisecond):
            # Update movement animation
            pass

        def tick_idle(self, time_delta: Millisecond):
            # Update idle animation
            pass
    ```
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Self

from nextrpg.core import Direction, Millisecond
from nextrpg.draw_on_screen import Drawing
from nextrpg.model import export


@export
@dataclass(frozen=True)
class CharacterDrawing(ABC):
    """
    Abstract interface for drawing characters on screen.

    This abstract base class defines the contract that all character
    drawing implementations must follow. It provides methods for
    character orientation, movement animation, and idle animation
    updates.

    The class is designed to be immutable, with all methods returning
    new instances rather than modifying the current state. This ensures
    thread safety and predictable behavior in the game loop.

    Arguments:
        `direction`: Initial character direction.

    Example:
        ```python
        from nextrpg.character_drawing import CharacterDrawing
        from nextrpg.core import Direction

        class MyCharacter(CharacterDrawing):
            def drawing(self):
                return self._get_current_drawing()

            def turn(self, direction: Direction):
                return self._with_direction(direction)
        ```
    """

    direction: Direction

    @cached_property
    @abstractmethod
    def drawing(self) -> Drawing:
        """
        Get the character's current drawing representation.

        This method should return the appropriate drawing based on
        the character's current state, direction, and animation frame.
        The drawing should reflect the character's current appearance
        including any active animations.

        Returns:
            `Drawing`: The character's current drawing representation.

        Example:
            ```python
            drawing = character.drawing
            # Use drawing for rendering
            ```
        """

    @abstractmethod
    def turn(self, direction: Direction) -> Self:
        """
        Turn the character to face a specified direction.

        This method should handle direction changes and return a new
        character instance with the updated direction. The method
        may also trigger direction-specific animations or state changes.

        Arguments:
            `direction`: The new direction the character should face.

        Returns:
            `CharacterDrawing`: A new character instance with the
                updated direction.

        Example:
            ```python
            # Turn character to face up
            character = character.turn(Direction.UP)
            ```
        """

    @abstractmethod
    def tick_move(self, time_delta: Millisecond) -> Self:
        """
        Update the character's movement animation state.

        This method should advance the character's movement animation
        based on the elapsed time. It's called when the character
        is actively moving.

        Arguments:
            `time_delta`: The amount of time that has passed since the
                last update in milliseconds.

        Returns:
            `CharacterDrawing`: A new character instance with updated
                movement animation state.

        Example:
            ```python
            # Update movement animation
            character = character.tick_move(time_delta)
            ```
        """

    @abstractmethod
    def tick_idle(self, time_delta: Millisecond) -> Self:
        """
        Update the character's idle animation state.

        This method should advance the character's idle animation
        based on the elapsed time. It's called when the character
        is not moving.

        Arguments:
            `time_delta`: The amount of time that has passed since the
                last update in milliseconds.

        Returns:
            `CharacterDrawing`: A new character instance with updated
                idle animation state.

        Example:
            ```python
            # Update idle animation
            character = character.tick_idle(time_delta)
            ```
        """
