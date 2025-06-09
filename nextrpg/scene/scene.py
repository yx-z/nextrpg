"""
Scene is an interface of all game interactions like exploration, menu, etc..
"""

from abc import ABC, abstractmethod

from nextrpg.common_types import Millisecond
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.event.pygame_event import PygameEvent


class Scene(ABC):
    """
    Abstract base class representing a game scene.

    This class defines the interface for game scenes, providing methods for
    handling events and drawing content on the screen. All game scenes must
    implement these methods.
    """

    @abstractmethod
    def event(self, event: PygameEvent) -> None:
        """
        Handles events for the scene.

        The recommended implementation is via `@singledispatchmethod`.
        And implement events of interesting `nextrpg.event.pygame_event` types.

        ```python
        class MyScene(Scene):
            @singledispatchmethod
            def event(self, event: PygameEvent) -> None:
                pass

            @event.register
            def _on_key_press_down(self, event: KeyPressDown) -> None:
                ...

            @event.register
            def _on_key_press_up(self, event: KeyPressUp) -> None:
                ...

            @event.register
            def _on_key_press_up(self, event: GuiResize | Quit) -> None:
                ...
        ```

        Arguments:
            `event`: The pygame event to process

        Returns:
            `None`
        """

    @abstractmethod
    def draw_on_screen(self, time_delta: Millisecond) -> list[DrawOnScreen]:
        """
        Generates the list of drawings to be rendered on screen.

        Arguments:
            `time_delta`: Time has elapsed since the last frame in milliseconds.

        Returns:
           `list[DrawOnScreen]`: objects to be rendered
        """
