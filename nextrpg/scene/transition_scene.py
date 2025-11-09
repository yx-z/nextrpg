from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import override

from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.core.util import background_thread
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
    intermediary: AnimationOnScreenLike = field(
        default_factory=lambda: screen_area().fill(config().window.background)
    )
    duration: Millisecond = field(
        default_factory=lambda: config().animation.default_timed_animation_duration
    )
    from_scene: Scene | Callable[[], Scene] = last_scene
    _: KW_ONLY = private_init_below()
    _fade_in: TimedAnimationOnScreens = default(
        lambda self: animate(self.intermediary, FadeIn, duration=self.duration)
    )
    _fade_out: TimedAnimationOnScreens = default(
        lambda self: animate(self.intermediary, FadeOut, duration=self.duration)
    )
    _to_scene: Future[Scene] | Scene = default(lambda self: self._init_to_scene)

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        # First phase: don't load to_scene yet.
        if not (fade_in := self._fade_in.tick(time_delta)).is_complete:
            return replace(self, from_scene=self._from_scene, _fade_in=fade_in)

        # Second phase: only show intermediary while loading to_scene.
        if isinstance(self._to_scene, Future) and not self._to_scene.done():
            intermediary = self.intermediary.tick(time_delta)
            return replace(self, _fade_in=fade_in, intermediary=intermediary)

        # Third Phase: start fading out once to_scene is loaded.
        if not (fade_out := self._fade_out.tick(time_delta)).is_complete:
            return replace(self, _fade_in=fade_in, _fade_out=fade_out)

        # Final phase: Transition complete.
        if isinstance(self._to_scene, Scene):
            return self._to_scene
        return self._to_scene.result()

    @override
    @cached_property
    def drawing_on_screens(self) -> list[DrawingOnScreen]:
        # First phase.
        if not self._fade_in.is_complete:
            return (
                self._from_scene.drawing_on_screens
                + self._fade_in.drawing_on_screens
            )

        # Second phase.
        if isinstance(self._to_scene, Future) and not self._to_scene.done():
            return self.intermediary.drawing_on_screens

        # Third phase.
        if isinstance(self._to_scene, Scene):
            to_scene = self._to_scene
        else:
            to_scene = self._to_scene.result()
        return to_scene.drawing_on_screens + self._fade_out.drawing_on_screens

    @cached_property
    def _from_scene(self) -> Scene:
        if callable(self.from_scene):
            return self.from_scene()
        return self.from_scene

    @cached_property
    def _init_to_scene(self) -> Scene | Future[Scene]:
        if callable(self.to_scene):
            return background_thread().submit(self.to_scene)
        return self.to_scene
