from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import override

from nextrpg.config.config import config
from nextrpg.core import Alpha, Millisecond, alpha_from_percentage
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.scene.scene import Scene
from nextrpg.scene.static_scene import StaticScene
from nextrpg.scene.transition_scene import TransitioningScene


@dataclass(frozen=True)
class TransitionTriple(Scene):
    from_scene: TransitioningScene
    intermediary: StaticScene
    to_scene: Scene
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _elapsed: Millisecond = 0

    def tick(self, time_delta: Millisecond) -> Scene:
        if (elapsed := self._elapsed + time_delta) < self._half_duration:
            from_scene = self.from_scene.tick_without_transition(time_delta)
            return replace(self, from_scene=from_scene, _elapsed=elapsed)

        to_scene = self.to_scene.tick(time_delta)
        if elapsed < self.duration:
            return replace(self, to_scene=to_scene, _elapsed=elapsed)
        return to_scene

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if self._elapsed < self._half_duration:
            alpha = alpha_from_percentage(self._elapsed / self._half_duration)
            intermediary_draws = self._intermediary_draw_on_screens(alpha)
            return self.from_scene.draw_on_screens + intermediary_draws

        remaining = self.duration - self._elapsed
        alpha = alpha_from_percentage(remaining / self._half_duration)
        intermediary_draws = self._intermediary_draw_on_screens(alpha)
        return self.to_scene.draw_on_screens + intermediary_draws

    def _intermediary_draw_on_screens(
        self, alpha: Alpha
    ) -> tuple[DrawOnScreen, ...]:
        return tuple(
            d.set_alpha(alpha) for d in self.intermediary.draw_on_screens
        )

    @cached_property
    def _half_duration(self) -> Millisecond:
        return self.duration / 2
