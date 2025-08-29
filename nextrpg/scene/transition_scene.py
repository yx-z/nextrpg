from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import override

from nextrpg.animation.fade import FadeIn, FadeOut
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.color import Color
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.gui.area import screen
from nextrpg.scene.scene import Scene


@dataclass_with_default(frozen=True)
class TransitionScene(Scene):
    from_scene: Scene
    to_scene: Scene
    intermediary: DrawingOnScreen | tuple[DrawingOnScreen, ...] | Color = field(
        default_factory=lambda: config().window.background
    )
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _: KW_ONLY = not_constructor_below()
    _fade_in: FadeIn = default(
        lambda self: FadeIn(self._intermediary, self.duration // 2)
    )
    _fade_out: FadeOut = default(
        lambda self: FadeOut(self._intermediary, self.duration // 2)
    )

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        fade_in = self._fade_in.tick(time_delta)
        if not fade_in.complete:
            return replace(self, _fade_in=fade_in)

        fade_out = self._fade_out.tick(time_delta)
        if fade_out.complete:
            return self.to_scene
        return replace(self, _fade_in=fade_in, _fade_out=fade_out)

    @cached_property
    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self._fade_in.complete:
            return (
                self.to_scene.drawing_on_screens
                + self._fade_out.drawing_on_screens
            )
        return (
            self.from_scene.drawing_on_screens
            + self._fade_in.drawing_on_screens
        )

    @property
    def _intermediary(self) -> DrawingOnScreen | tuple[DrawingOnScreen, ...]:
        if isinstance(self.intermediary, Color):
            return screen().fill(self.intermediary)
        return self.intermediary
