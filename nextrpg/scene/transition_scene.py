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
from nextrpg.game.game_state import GameState
from nextrpg.gui.screen_area import screen_area
from nextrpg.scene.scene import Scene

ToSceneAndState = Scene | tuple[Scene, GameState]


@dataclass_with_default(frozen=True)
class TransitionScene(Scene):
    to_scene_and_state: ToSceneAndState | Callable[[GameState], ToSceneAndState]
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
    _to_scene_and_state: (
        Future[tuple[Scene, GameState]] | tuple[Scene, GameState]
    ) | None = None

    @override
    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState]:
        # First phase: don't load to_scene yet.
        if not (fade_in := self._fade_in.tick(time_delta)).is_complete:
            ticked = replace(
                self, from_scene=self._from_scene, _fade_in=fade_in
            )
            return ticked, state

        # Second phase: start loading to_scene_and_state in the background.
        if self._to_scene_and_state:
            to_scene_and_state = self._to_scene_and_state
        else:
            if callable(self.to_scene_and_state):
                to_scene_and_state = background_thread().submit(
                    self.to_scene_and_state, state
                )
            else:
                to_scene_and_state = self.to_scene_and_state

        # Second phase: only show intermediary while loading to_scene.
        if (
            isinstance(to_scene_and_state, Future)
            and not to_scene_and_state.done()
        ):
            intermediary = self.intermediary.tick(time_delta)
            ticked = replace(
                self,
                _fade_in=fade_in,
                intermediary=intermediary,
                _to_scene_and_state=to_scene_and_state,
            )
            return ticked, state

        # Third Phase: start fading out once to_scene is loaded.
        if not (fade_out := self._fade_out.tick(time_delta)).is_complete:
            ticked = replace(
                self,
                _fade_in=fade_in,
                _fade_out=fade_out,
                _to_scene_and_state=to_scene_and_state,
            )
            return ticked, state

        # Final phase: Transition complete.
        assert (
            self._to_scene_and_state_result
        ), f"Require _to_scene_and_state. Got {self._to_scene_and_state}"
        if isinstance(self._to_scene_and_state_result, Scene):
            ticked = self._to_scene_and_state_result
        else:
            ticked, state = self._to_scene_and_state_result
        return ticked, state

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        # First phase.
        if not self._fade_in.is_complete:
            return (
                self._from_scene.drawing_on_screens
                + self._fade_in.drawing_on_screens
            )

        # Second phase.
        if (
            isinstance(self._to_scene_and_state, Future)
            and not self._to_scene_and_state.done()
        ):
            return self.intermediary.drawing_on_screens

        assert (
            self._to_scene_and_state_result
        ), f"Require _to_scene_and_state. Got {self._to_scene_and_state}"
        if isinstance(self._to_scene_and_state_result, Scene):
            to_scene = self._to_scene_and_state_result
        else:
            to_scene, _ = self._to_scene_and_state_result

        # Third phase.
        return to_scene.drawing_on_screens + self._fade_out.drawing_on_screens

    @cached_property
    def _to_scene_and_state_result(
        self,
    ) -> Scene | tuple[Scene, GameState] | None:
        if isinstance(self._to_scene_and_state, Future):
            return self._to_scene_and_state.result()
        return self._to_scene_and_state

    @cached_property
    def _from_scene(self) -> Scene:
        if callable(self.from_scene):
            return self.from_scene()
        return self.from_scene
