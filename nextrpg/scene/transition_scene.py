from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.config.config import config
from nextrpg.core import Millisecond, alpha_from_percentage
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.scene.scene import Scene


class TransitioningScene(Scene):
    def tick_without_transition(self, time_delta: Millisecond) -> Self:
        return self


@dataclass(frozen=True)
class TransitionScene(Scene):
    """
    Transition from one scene to another.

    Attributes:
        `from_scene`: The scene to transition from.

        `to_scene`: The scene to transition to.
    """

    from_scene: TransitioningScene
    to_scene: Scene
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _elapsed: Millisecond = 0

    def tick(self, time_delta: Millisecond) -> Scene:
        to_scene = self.to_scene.tick(time_delta)
        if (elapsed := self._elapsed + time_delta) > self.duration:
            return to_scene

        from_scene = self.from_scene.tick_without_transition(time_delta)
        return replace(
            self, _elapsed=elapsed, from_scene=from_scene, to_scene=to_scene
        )

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        alpha = alpha_from_percentage(self._elapsed / self.duration)
        to_scene_draws = tuple(
            d.set_alpha(alpha) for d in self.to_scene.draw_on_screens
        )
        return self.from_scene.draw_on_screens + to_scene_draws
