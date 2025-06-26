"""
Scene is an interface of all game interactions like exploration, menu, etc..
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable

from nextrpg.config import config
from nextrpg.core import Millisecond
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.event.pygame_event import PygameEvent


class Scene:
    """
    Base class representing a game scene.

    This class defines the interface for game scenes, providing methods for
    handling events and drawing content on the screen. All game scenes must
    implement these methods.

    Attributes:
        `draw_on_screens`: The list of drawings to be rendered on screen.
    """

    draw_on_screens: list[DrawOnScreen]

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

    def step(self, time_delta: Millisecond) -> Scene:
        """
        Update the scene state for a single game step/frame.

        Progresses the scene state based on the elapsed time since the
        last update, handling animations, movements,
        and other time-dependent changes.

        Args:
            `time_delta`: The time that has passed since the last update,
                used for calculating time-based changes.

        Returns:
            `Scene`: The updated scene state after the time step.
        """
        return self


_scenes = OrderedDict[Callable[..., Scene], Scene]()


def get_scene[**P](
    fun: Callable[P, Scene], /, *args: P.args, **kwargs: P.kwargs
) -> Scene:
    if fun in _scenes:
        _scenes.move_to_end(fun, last=False)
        return _scenes[fun]
    s = fun(*args, **kwargs)
    while len(_scenes) >= config().resource.scene_cache_size:
        _scenes.popitem(last=False)
    _scenes[fun] = s
    return s
