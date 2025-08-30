from __future__ import annotations

from collections.abc import Callable, Generator
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self, override

from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.scene.rpg_event.eventful_scene import EventfulScene
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class RpgEventScene[R = None](Scene):
    generator: EventGenerator
    scene: EventfulScene

    @cached_property
    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self.scene.drawing_on_screens + self.add_ons

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        ticked = replace(self, scene=self.scene.tick_without_event(time_delta))
        return self.tick_after_scene(time_delta, ticked)

    def tick_after_scene(self, time_delta: Millisecond, ticked: Self) -> Scene:
        return ticked

    @property
    def add_ons(self) -> tuple[DrawingOnScreen, ...]:
        return ()


def register_rpg_event_scene[R, **P](
    cls: type[RpgEventScene[Any]],
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

type EventCallable = Callable[[EventGenerator, EventfulScene], RpgEventScene]
type EventGenerator = Generator[EventCallable, Any, bool | None]
