from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.core.dataclass_with_default import dataclass_with_default
from nextrpg.drawing.color import alpha_from_percentage
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen


@dataclass_with_default(frozen=True)
class Fade(TimedAnimationOnScreens, ABC):
    @cached_property
    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self._percentage <= 0:
            return ()
        drawing_on_screens = super().drawing_on_screens
        if self._percentage >= 1:
            return drawing_on_screens
        alpha = alpha_from_percentage(self._percentage)
        return tuple(d.with_alpha(alpha) for d in drawing_on_screens)

    @property
    @abstractmethod
    def _percentage(self) -> float: ...


@dataclass(frozen=True)
class FadeIn(Fade):
    final_alpha_percentage: float = 1.0

    @override
    @cached_property
    def _percentage(self) -> float:
        return self._timer.completed_percentage * self.final_alpha_percentage


@dataclass(frozen=True)
class FadeOut(Fade):
    final_alpha_percentage: float = 0.0

    @override
    @cached_property
    def _percentage(self) -> float:
        return self._timer.remaining_percentage * (
            1 - self.final_alpha_percentage
        )
