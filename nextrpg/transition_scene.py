"""
Transition scene system for NextRPG.

This module provides transition scene functionality for smooth
scene changes in NextRPG games. It includes the `TransitionScene`
class which handles crossfade transitions between scenes.

The transition scene system features:
- Crossfade transitions between scenes
- Configurable transition duration
- Alpha-based blending
- Intermediary scene support

Example:
    ```python
    from nextrpg.transition_scene import TransitionScene
    from nextrpg.scene import Scene
    from nextrpg.core import Millisecond

    # Create transition scene
    transition = TransitionScene(
        from_scene=current_scene,
        intermediary=intermediary_scene,
        to_scene=next_scene,
        duration=Millisecond(1000)
    )

    # Update transition in game loop
    scene = transition.tick(time_delta)
    ```
"""

from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.core import Alpha, Millisecond, alpha_from_percentage
from nextrpg.draw_on_screen import DrawOnScreen
from nextrpg.global_config import config
from nextrpg.model import export
from nextrpg.scene import Scene


@export
class TransitioningScene(Scene):
    """
    Base class for scenes that support transitions.

    This class provides a base for scenes that can participate
    in transitions. It includes a method for updating without
    triggering transition effects.

    Example:
        ```python
        class MyScene(TransitioningScene):
            def tick_without_transition(self, time_delta):
                # Update scene without transition effects
                return self
        ```
    """

    def tick_without_transition(self, time_delta: Millisecond) -> Self:
        """
        Update the scene without triggering transition effects.

        Arguments:
            `time_delta`: The elapsed time in milliseconds.

        Returns:
            `TransitioningScene`: Updated scene instance.
        """
        return self


@export
@dataclass(frozen=True)
class TransitionScene(Scene):
    """
    Scene that handles transitions between other scenes.

    This class provides crossfade transition functionality between
    scenes. It manages the transition timing and alpha blending
    of drawing resources from multiple scenes.

    Arguments:
        `from_scene`: The scene to transition from.

        `intermediary`: The intermediary scene used during transition.

        `to_scene`: The scene to transition to.

        `duration`: The duration of the transition in milliseconds.
            Defaults to the global transition duration.

        `_elapsed`: Internal elapsed time tracking.

    Example:
        ```python
        from nextrpg.transition_scene import TransitionScene
        from nextrpg.scene import Scene
        from nextrpg.core import Millisecond

        # Create transition scene
        transition = TransitionScene(
            from_scene=current_scene,
            intermediary=intermediary_scene,
            to_scene=next_scene,
            duration=Millisecond(2000)
        )

        # Update in game loop
        scene = transition.tick(time_delta)
        ```
    """

    from_scene: TransitioningScene
    intermediary: Scene
    to_scene: Scene
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _elapsed: Millisecond = 0

    def tick(self, time_delta: Millisecond) -> Scene:
        """
        Update the transition scene.

        Advances the transition and updates the involved scenes.
        Returns the appropriate scene based on transition progress.

        Arguments:
            `time_delta`: The elapsed time in milliseconds.

        Returns:
            `Scene`: The current scene (transition or target scene).
        """
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
        """
        Get the current drawing resources for rendering.

        Returns blended drawing resources from the involved scenes
        based on the transition progress.

        Returns:
            `tuple[DrawOnScreen, ...]`: The current drawing resources.
        """
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
        """
        Get intermediary scene drawings with alpha blending.

        Arguments:
            `alpha`: The alpha value for blending.

        Returns:
            `tuple[DrawOnScreen, ...]`: Alpha-blended intermediary drawings.
        """
        return tuple(
            d.set_alpha(alpha) for d in self.intermediary.draw_on_screens
        )

    @cached_property
    def _half_duration(self) -> Millisecond:
        """
        Get half of the transition duration.

        Returns:
            `Millisecond`: Half of the total transition duration.
        """
        return self.duration // 2
