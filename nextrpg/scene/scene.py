"""
Base scene interface and management for `NextRPG`.

This module provides the foundational scene system for `NextRPG` games. It
defines the `Scene` base class that all game scenes must inherit from,
providing a consistent interface for scene management, event handling, and
rendering.

The scene system provides:
- Abstract base class for all game scenes
- Event handling interface for user input
- Time-based scene updates for animations
- Drawing management with screen shifting
- Scene state management and transitions

This module establishes the contract that all scene implementations must
follow, ensuring consistent behavior across different types of game scenes.
"""

from functools import cached_property
from typing import override

from nextrpg.core.coordinate import Coordinate
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.event.pygame_event import PygameEvent
from nextrpg.draw.animated import Animated


class Scene(Animated):
    """
    Base class representing a game scene.

    This abstract base class defines the interface that all game scenes must
    implement. It provides methods for event handling, time-based updates, and
    drawing management.

    The scene system is designed to be immutable, with all methods returning
    new scene instances rather than modifying the current state. This ensures
    thread safety and predictable behavior.

    Scenes can represent various game states such as:
    - Game world exploration
    - Menu systems
    - Dialog sequences
    - Battle scenes
    - Transition effects
    """

    @property
    def draw_on_screen_shift(self) -> Coordinate | None:
        """
        Get the offset applied to all drawings before GUI scaling.

        This property provides a coordinate offset that is applied to
        all drawings in the scene. It's commonly used for camera
        positioning, such as centering the player on screen in map
        scenes.

        Returns:
            `Coordinate | None`: The shift offset for all drawings,
                or `None` if no shift is applied.

        Example:
            ```python
            # Center the scene on the player
            def draw_on_screen_shift(self):
                return Coordinate(-player.x + screen_width/2,
                                -player.y + screen_height/2)
            ```
        """
        return None

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the drawables to be rendered on screen with shift applied.

        This property returns all drawable objects for the scene,
        with the `draw_on_screen_shift` applied if specified.
        The shift is applied before GUI scaling to ensure proper
        positioning.

        Returns:
            `tuple[DrawOnScreen, ...]`: The drawables to be rendered.

        Example:
            ```python
            def draw_on_screens_before_shift(self):
                return (player_sprite, background, ui_elements)
            ```
        """
        if self.draw_on_screen_shift:
            return tuple(
                d.shift(self.draw_on_screen_shift)
                for d in self.draw_on_screens_before_shift
            )
        return self.draw_on_screens_before_shift

    @property
    def draw_on_screens_before_shift(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the drawables before shift is applied.

        This method should be overridden by subclasses to provide
        the actual drawable objects for the scene. The shift will
        be applied automatically by `draw_on_screens`.

        Returns:
            `tuple[DrawOnScreen, ...]`: The drawables before shift.
        """
        return ()

    def event(self, event: PygameEvent) -> Scene:
        """
        Handle events for the scene.

        This method processes pygame events and returns an updated
        scene state. The recommended implementation uses
        `@singledispatchmethod` to handle different event types
        efficiently.

        Arguments:
            `event`: The pygame event to process.

        Returns:
            `Scene`: The updated scene state after processing the event.

        Example:
            ```python
            from functools import singledispatchmethod
            from nextrpg.event.pygame_event import KeyPressDown, KeyPressUp

            class MyScene(Scene):
                @singledispatchmethod
                def event(self, event: PygameEvent) -> Scene:
                    return self

                @event.register
                def _on_key_press_down(self, event: KeyPressDown) -> Scene:
                    # Handle key press
                    return self

                @event.register
                def _on_key_press_up(self, event: KeyPressUp) -> Scene:
                    # Handle key release
                    return self
            ```
        """
        return self
