from dataclasses import KW_ONLY, field, replace
from math import ceil
from typing import override

from nextrpg.config import config
from nextrpg.core import Alpha, Millisecond
from nextrpg.draw_on_screen import DrawOnScreen, screen
from nextrpg.model import Model, internal_field
from nextrpg.scene.scene import Scene


class TransitionScene(Model, Scene):
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
    transition_drawings: list[DrawOnScreen] = field(
        default_factory=lambda: [screen().fill(config().gui.background_color)]
    )
    _: KW_ONLY = field()
    _elapsed: Millisecond = internal_field(0)

    @property
    @override
    def draw_on_screens(self) -> list[DrawOnScreen]:
        if not self.transition_drawings:
            return self.from_scene.draw_on_screens + self._to_scene_drawings

        if self._is_before_half_transition:
            transitions = [
                replace(d, drawing=d.drawing.set_alpha(self._alpha))
                for d in self.transition_drawings
            ]
            return self.from_scene.draw_on_screens + transitions
        return self.transition_drawings + self._to_scene_drawings

    def step(self, time_delta: Millisecond) -> Scene:
        if self._elapsed > self.duration:
            return self.to_scene
        return replace(self, _elapsed=self._elapsed + time_delta)

    @property
    def _to_scene_drawings(self) -> list[DrawOnScreen]:
        return [
            replace(d, drawing=d.drawing.set_alpha(self._alpha))
            for d in self.to_scene.draw_on_screens
        ]

    @property
    def _alpha(self) -> Alpha:
        return _scale(self._alpha_percentage)

    @property
    def _alpha_percentage(self) -> float:
        if not self.transition_drawings:
            return self._elapsed / self.duration

        if self._is_before_half_transition:
            return self._elapsed / self._half_duration
        return (self.duration - self._elapsed) / self._half_duration

    @property
    def _half_duration(self) -> Millisecond:
        return self.duration / 2

    @property
    def _is_before_half_transition(self) -> bool:
        return self._elapsed < self._half_duration


def _scale(alpha_percentage: float) -> Alpha:
    return ceil(255 * alpha_percentage)
