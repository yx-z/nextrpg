from collections.abc import Callable
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import override

from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import (
    AnimationOnScreenLike,
    animate,
)
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.game.game_loop import last_scene
from nextrpg.gui.screen_area import screen_area
from nextrpg.scene.scene import Scene


@dataclass_with_default(frozen=True)
class TransitionScene(Scene):
    to_scene: Scene | Callable[[], Scene]
    intermediary: DrawingOnScreen | tuple[DrawingOnScreen, ...] = field(
        default_factory=lambda: screen_area().fill(config().window.background)
    )
    duration: Millisecond = field(
        default_factory=lambda: config().timing.transition_scene_duration
    )
    _: KW_ONLY = private_init_below()
    _from_scene_member: Callable[[], Scene] | Scene = last_scene
    _fade_in: AnimationOnScreenLike = default(
        lambda self: animate(
            self.intermediary, FadeIn, duration=self.duration // 2
        )
    )
    _fade_out: AnimationOnScreenLike = default(
        lambda self: animate(
            self.intermediary, FadeOut, duration=self.duration // 2
        )
    )

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        # First half: don't load to_scene yet.
        if not (fade_in := self._fade_in.tick(time_delta)).is_complete:
            return replace(
                self, _from_scene_member=self._from_scene, _fade_in=fade_in
            )

        # Second half.
        if not (fade_out := self._fade_out.tick(time_delta)).is_complete:
            return replace(
                self,
                to_scene=self._to_scene,
                _fade_in=fade_in,
                _fade_out=fade_out,
            )

        # Transition complete.
        return self._to_scene

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        # First half.
        if self._fade_in.is_complete:
            return (
                self._to_scene.drawing_on_screens
                + self._fade_out.drawing_on_screens
            )
        # Second half.
        return (
            self._from_scene.drawing_on_screens
            + self._fade_in.drawing_on_screens
        )

    @cached_property
    def _from_scene(self) -> Scene:
        if callable(self._from_scene_member):
            return self._from_scene_member()
        return self._from_scene_member

    @cached_property
    def _to_scene(self) -> Scene:
        if callable(self.to_scene):
            return self.to_scene()
        return self.to_scene
