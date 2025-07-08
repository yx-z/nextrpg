from dataclasses import replace
from functools import cached_property
from typing import override

from nextrpg.core import Millisecond
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.model import instance_init, dataclass_with_instance_init
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene


@dataclass_with_instance_init
class TransitionTriple(Scene):
    from_scene: Scene
    intermediary: Scene
    to_scene: Scene
    _from_and_intermediary: TransitionScene | Scene = instance_init(
        lambda self: TransitionScene(self.from_scene, self.intermediary)
    )
    _intermediary_and_to: TransitionScene | Scene = instance_init(
        lambda self: TransitionScene(self.intermediary, self.to_scene)
    )

    def tick(self, time_delta: Millisecond) -> Scene:
        if self._before_intermediary:
            from_and_intermediary = self._from_and_intermediary.tick(time_delta)
            return replace(self, _from_and_intermediary=from_and_intermediary)

        if self._intermediary_and_to is not self.to_scene:
            intermediary_and_to = self._intermediary_and_to.tick(time_delta)
            return replace(self, _intermediary_and_to=intermediary_and_to)

        return self.to_scene

    @cached_property
    @override
    def _draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if self._before_intermediary:
            return self._from_and_intermediary.draw_on_screens
        return self._intermediary_and_to.draw_on_screens

    @cached_property
    def _before_intermediary(self) -> DrawOnScreen:
        return self._from_and_intermediary is not self.intermediary
