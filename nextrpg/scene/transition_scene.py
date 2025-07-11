from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import override

from nextrpg.config import config
from nextrpg.core import Alpha, Millisecond
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
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
        default_factory=lambda: config().transition.duration
    )
    _elapsed: Millisecond = 0

    def tick(self, time_delta: Millisecond) -> Scene:
        tick_to_scene = self.to_scene.tick(time_delta)
        if (total_elapsed := self._elapsed + time_delta) > self.duration:
            return tick_to_scene
        return replace(
            self,
            _elapsed=total_elapsed,
            from_scene=self.from_scene.tick(time_delta),
            to_scene=tick_to_scene,
        )

    @cached_property
    def _to_scene_drawings(self) -> tuple[DrawOnScreen, ...]:
        return tuple(
            DrawOnScreen(d.top_left, d.drawing.set_alpha(self._alpha))
            for d in self.to_scene.draw_on_screens
        )

    @cached_property
    def _alpha(self) -> Alpha:
        return _scale(self._alpha_percentage)

    @cached_property
    def _alpha_percentage(self) -> float:
        return self._elapsed / self.duration

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self.from_scene.draw_on_screens + self._to_scene_drawings


def _scale(alpha_percentage: float) -> Alpha:
    return int(255 * alpha_percentage)
