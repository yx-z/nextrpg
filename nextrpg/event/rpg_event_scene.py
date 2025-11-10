from collections.abc import Callable, Generator
from dataclasses import dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Any, Literal, Self, override

from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.scene.scene import Scene

if TYPE_CHECKING:
    from nextrpg.event.eventful_scene import EventfulScene


@dataclass(frozen=True)
class RpgEventScene(Scene):
    generator: EventGenerator
    parent: EventfulScene

    @cached_property
    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return (
            self.parent.drawing_on_screens
            + self.drawing_on_screens_after_parent
        )

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        parent = self.parent.tick_without_event(time_delta)
        ticked = replace(self, parent=parent)
        return self._tick_after_parent(time_delta, ticked)

    @cached_property
    def drawing_on_screens_after_parent(self) -> tuple[DrawingOnScreen, ...]:
        return ()

    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self
    ) -> Scene:
        return ticked


def register_rpg_event_scene[R, **P](
    cls: type[RpgEventScene],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(f: Callable[P, R]) -> Callable[P, R]:
        def decorated(*args: P.args, **kwargs: P.kwargs) -> R:
            return lambda generator, scene: cls(
                generator, scene, *args, **kwargs
            )

        registered_rpg_event_scenes[f.__name__] = decorated
        return decorated

    return decorate


registered_rpg_event_scenes: dict[str, Callable[..., None]] = {}


class _DontRestartEvent:
    pass


DONT_RESTART_EVENT = _DontRestartEvent()

type EventCallable = Callable[[EventGenerator, EventfulScene], RpgEventScene]
type EventGenerator = Generator[
    EventCallable, Any, Any | Literal[DONT_RESTART_EVENT] | None
]
