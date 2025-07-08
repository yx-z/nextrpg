"""
Scene is an interface of all game interactions like exploration, menu, etc.
"""

from functools import cached_property
from collections.abc import Iterable

from nextrpg.core import Millisecond
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.coordinate import Coordinate
from nextrpg.event.pygame_event import PygameEvent


class Scene:
    """
    Base class representing a game scene.

    This class defines the interface for game scenes, providing methods for
    handling events and drawing content on the screen. All game scenes must
    implement these methods.
    """

    @cached_property
    def draw_on_screen_shift(self) -> Coordinate:
        """
        The offset of all drawings applied after `draw_on_screens` (before GUI
        scaling), so that the drawings are shifted correctly on screen.

        This is useful for e.g., map to center the player on screen.

        Returns:
            `Coordinate`: The shift offset of all drawings.
        """
        return Coordinate(0, 0)

    @cached_property
    def draw_on_screens_shifted(self) -> tuple[DrawOnScreen, ...]:
        """
        Get the tuple of drawables to be rendered on the screen, shifted by
        `self.draw_on_screen_shift`.

        Returns:
            `tuple[DrawOnScreen, ...]`: The tuple of drawables to be rendered.
        """
        return tuple(
            d.shift(self.draw_on_screen_shift) for d in self._draw_on_screens
        )

    @cached_property
    def _draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return ()

    def event(self, event: PygameEvent) -> Scene:
        """
        Handles events for the scene.

        The recommended implementation is via `@singledispatchmethod`.
        And implement events of interesting `nextrpg.event.pygame_event` types.

        ```python
        class MyScene(Scene):
            @singledispatchmethod
            def event(self, event: PygameEvent) -> Scene:
                pass

            @event.register
            def _on_key_press_down(self, event: KeyPressDown) -> Scene:
                ...

            @event.register
            def _on_key_press_up(self, event: KeyPressUp) -> Scene:
                ...

            @event.register
            def _on_key_press_up(self, event: GuiResize | Quit) -> Scene:
                ...
        ```

        Arguments:
            `event`: The pygame event to process

        Returns:
            `Scene`: The updated scene state after processing the event.
        """
        return self

    def tick(self, time_delta: Millisecond) -> Scene:
        """
        Update the scene state for a single game step/frame.

        Progresses the scene state based on the elapsed time since the
        last update, handling animations, movements,
        and other time-dependent changes.

        Arguments:
            `time_delta`: The time that has passed since the last update,
                used for calculating time-based changes.

        Returns:
            `Scene`: The updated scene state after the time step.
        """
        return self
