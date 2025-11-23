from abc import abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.geometry.scaling import (
    HeightScaling,
    WidthAndHeightScaling,
    WidthScaling,
)


@dataclass(frozen=True)
class Scale(TimedAnimationGroup):

    @override
    @cached_property
    def drawing(self) -> DrawingGroup:
        group = tuple(
            relative_drawing * self.scaling
            for relative_drawing in super().drawing.resources
        )
        return DrawingGroup(group)

    @property
    @abstractmethod
    def scaling(
        self,
    ) -> WidthScaling | HeightScaling | WidthAndHeightScaling: ...


@dataclass(frozen=True, kw_only=True)
class ScaleTo(Scale):
    scale_to: WidthScaling | HeightScaling | WidthAndHeightScaling

    @override
    @cached_property
    def scaling(self) -> WidthScaling | HeightScaling | WidthAndHeightScaling:
        scaling = (
            1 + (self.scale_to.value - 1) * self._timer.completed_percentage
        )
        return type(self.scale_to)(scaling)


@dataclass(frozen=True, kw_only=True)
class ScaleFrom(Scale):
    scale_from: WidthScaling | HeightScaling | WidthAndHeightScaling = (
        WidthAndHeightScaling(0)
    )

    @override
    @cached_property
    def scaling(self) -> WidthScaling | HeightScaling | WidthAndHeightScaling:
        scaling = (
            self.scale_from.value
            + (1 - self.scale_from.value) * self._timer.completed_percentage
        )
        return type(self.scale_from)(scaling)
