from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.core.util import Percentage
from nextrpg.drawing.color import alpha_from_percentage
from nextrpg.drawing.drawing_group import DrawingGroup


@dataclass(frozen=True)
class Fade(TimedAnimationGroup, ABC):
    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        alpha = alpha_from_percentage(self.alpha_percentage)
        return super().drawing.alpha(alpha)

    @property
    @abstractmethod
    def alpha_percentage(self) -> Percentage: ...


@dataclass(frozen=True)
class FadeIn(Fade):
    final_alpha_percentage: Percentage = 1.0

    @override
    @cached_property
    def alpha_percentage(self) -> Percentage:
        return self._timer.completed_percentage * self.final_alpha_percentage


@dataclass(frozen=True)
class FadeOut(Fade):
    final_alpha_percentage: Percentage = 0.0

    @override
    @cached_property
    def alpha_percentage(self) -> Percentage:
        final_alpha_remaining = 1 - self.final_alpha_percentage
        return self._timer.remaining_percentage * final_alpha_remaining
