from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import override

from nextrpg.config import config
from nextrpg.core import Alpha, Millisecond
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.scene.scene import Scene


@dataclass
class TransitionScene(Scene):
    """
    Transition from one scene to another.

    Attributes:
        `from_scene`: The scene to transition from.

        `to_scene`: The scene to transition to.
    """

    from_scene: Scene
    to_scene: Scene
    duration: Millisecond = field(
        default_factory=lambda: config().transition.transition_duration
    )
    _elapsed: Millisecond = 0

    @cached_property
    @override
    def draw_on_screens(self) -> list[DrawOnScreen]:
        return self.from_scene.draw_on_screens + self._to_scene_drawings

    def step(self, time_delta: Millisecond) -> Scene:
        return (
            self.to_scene
            if (total_elapsed := self._elapsed + time_delta) > self.duration
            else replace(self, _elapsed=total_elapsed)
        )

    @cached_property
    def _to_scene_drawings(self) -> list[DrawOnScreen]:
        return [
            DrawOnScreen(d.top_left, d.drawing.set_alpha(self._alpha))
            for d in self.to_scene.draw_on_screens
        ]

    @cached_property
    def _alpha(self) -> Alpha:
        return _scale(self._alpha_percentage)

    @cached_property
    def _alpha_percentage(self) -> float:
        return self._elapsed / self.duration


def _scale(alpha_percentage: float) -> Alpha:
    return int(255 * alpha_percentage)
