from dataclasses import replace
from functools import cached_property
from typing import override

from nextrpg.core import Millisecond
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.model import instance_init, register_instance_init
from nextrpg.scene.scene import Scene
from nextrpg.scene.transition_scene import TransitionScene


@register_instance_init
class TransitionChain(Scene):
    from_scene: Scene
    intermediary_scene: Scene
    to_scene: Scene
    _from_and_intermediary: TransitionScene | Scene = instance_init(
        lambda self: TransitionScene(self.from_scene, self.intermediary_scene)
    )
    _intermediary_and_to: TransitionScene | Scene = instance_init(
        lambda self: TransitionScene(self.intermediary_scene, self.to_scene)
    )

    def tick(self, time_delta: Millisecond) -> Scene:
        if isinstance(self._from_and_intermediary, TransitionScene):
            tick = self._from_and_intermediary.tick(time_delta)
            return replace(self, _from_and_intermediary=tick)

        if isinstance(self._intermediary_and_to, TransitionScene):
            tick = self._intermediary_and_to.tick(time_delta)
            return replace(self, _intermediary_and_to=tick)

        return self._intermediary_and_to

    @cached_property
    @override
    def _draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return (
            self._from_and_intermediary.draw_on_screens_shifted
            if isinstance(self._from_and_intermediary, TransitionScene)
            else self._intermediary_and_to.draw_on_screens_shifted
        )
