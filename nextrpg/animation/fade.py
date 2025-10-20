from abc import abstractmethod
from dataclasses import dataclass, field
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.config.config import config
from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import alpha_from_percentage
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup


@dataclass(frozen=True)
class Fade(TimedAnimationGroup):
    duration: Millisecond = field(
        default_factory=lambda: config().timing.fade_duration
    )

    @override
    @cached_property
    def drawing(self) -> Drawing | DrawingGroup:
        alpha = alpha_from_percentage(self._percentage)
        return super().drawing.alpha(alpha)

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
        final_alpha_remaining = 1 - self.final_alpha_percentage
        return self._timer.remaining_percentage * final_alpha_remaining
