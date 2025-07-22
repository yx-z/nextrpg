"""
Transition scene system for `NextRPG`.

This module provides transition scene functionality for smooth scene changes in
`NextRPG` games. It includes the `TransitionScene` class which handles
crossfade transitions between scenes.

The transition scene system features:
- Crossfade transitions between scenes
- Configurable transition duration
- Alpha-based blending
- Intermediary scene support
"""

from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import override

from nextrpg.core.model import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.color import Rgba
from nextrpg.draw.draw_on_screen import DrawOnScreen
from nextrpg.draw.fade import FadeIn, FadeOut
from nextrpg.global_config.global_config import config
from nextrpg.gui.area import screen
from nextrpg.scene.scene import Scene


@dataclass_with_instance_init
class TransitionScene(Scene):
    """
    Scene that handles transitions between other scenes.

    This class provides crossfade transition functionality between scenes. It
    manages the transition timing and alpha blending of drawing resources from
    multiple scenes.

    Arguments:
        `from_scene`: The scene to transition from.
        `intermediary`: The intermediary scene used during transition.
        `to_scene`: The scene to transition to.
        `duration`: The duration of the transition in milliseconds. Defaults to
            the global transition duration.
        `_elapsed`: Internal elapsed time tracking.
    """

    from_scene: Scene
    to_scene: Scene
    intermediary: DrawOnScreen | tuple[DrawOnScreen, ...] | Rgba = field(
        default_factory=lambda: config().gui.background_color
    )
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _: KW_ONLY = not_constructor_below()
    _fade_in: FadeIn = instance_init(
        lambda self: FadeIn(
            resource=self._intermediary, duration=self._half_duration
        )
    )
    _fade_out: FadeOut = instance_init(
        lambda self: FadeOut(
            resource=self._intermediary, duration=self._half_duration
        )
    )

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        fade_in = self._fade_in.tick(time_delta)
        if not fade_in.complete:
            from_scene = self.from_scene.tick(time_delta)
            return replace(self, from_scene=from_scene, _fade_in=fade_in)

        fade_out = self._fade_out.tick(time_delta)
        to_scene = self.to_scene.tick(time_delta)
        if fade_out.complete:
            return to_scene
        return replace(
            self, to_scene=to_scene, _fade_in=fade_in, _fade_out=fade_out
        )

    @cached_property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if self._fade_in.complete:
            return (
                self.to_scene.draw_on_screens + self._fade_out.draw_on_screens
            )
        return self.from_scene.draw_on_screens + self._fade_in.draw_on_screens

    @property
    def _half_duration(self) -> Millisecond:
        return self.duration // 2

    @property
    def _intermediary(self) -> DrawOnScreen | tuple[DrawOnScreen, ...]:
        if isinstance(self.intermediary, Rgba):
            return screen().fill(color=self.intermediary)
        return self.intermediary
