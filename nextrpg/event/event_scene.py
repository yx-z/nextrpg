from collections.abc import Callable, Generator
from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Literal, Self, override

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.game.game_state import GameState
from nextrpg.scene.scene import Scene

if TYPE_CHECKING:
    from nextrpg.event.eventful_scene import EventfulScene


@dataclass(frozen=True)
class EventScene(Scene):
    parent: EventfulScene

    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        return (
            self.parent.drawing_on_screens
            + self.drawing_on_screens_after_parent
        )

    @override
    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState]:
        parent, state = self.parent.tick_without_event(time_delta, state)
        ticked = replace(self, parent=parent)
        return self._tick_after_parent(time_delta, ticked, state)

    @cached_property
    def drawing_on_screens_after_parent(self) -> DrawingOnScreens:
        return DrawingOnScreens()

    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self, state: GameState
    ) -> tuple[Scene, GameState]:
        return ticked, state


def register_rpg_event_scene[R, **P](
    cls: type[EventScene],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(f: Callable[P, R]) -> Callable[P, R]:
        def decorated(*args: P.args, **kwargs: P.kwargs) -> R:
            return lambda scene: cls(scene, *args, **kwargs)

        registered_rpg_event_scenes[f.__name__] = decorated
        return decorated

    return decorate


registered_rpg_event_scenes: dict[str, Callable[..., None]] = {}


class _DontRestartEvent:
    pass


DISMISS_EVENT = _DontRestartEvent()

type EventCallable = Callable[[EventfulScene], EventScene]
type EventCompletion = Literal[DISMISS_EVENT] | Any | None
type EventGenerator = Generator[EventCallable, Any, EventCompletion]
