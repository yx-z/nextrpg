from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.core.dataclass_with_default import dataclass_with_default
from nextrpg.drawing.color import alpha_from_percentage
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup


@dataclass_with_default(frozen=True)
class Fade(TimedAnimationGroup):
    @override
    @cached_property
    def drawing(self) -> Drawing | DrawingGroup:
        if self._percentage <= 0:
            return DrawingGroup(())
        drawing = super().drawing
        if self._percentage >= 1:
            return drawing
        alpha = alpha_from_percentage(self._percentage)
        return drawing.alpha(alpha)

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
