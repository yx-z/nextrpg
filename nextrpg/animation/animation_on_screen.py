from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, TypeVar, override

from nextrpg.animation.animation import Animation
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.sizable_drawing_on_screens import SizableDrawingOnScreens
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.geometry.sizable import Sizable


class AnimationOnScreen(Sizable, ABC):
    @property
    @abstractmethod
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def is_complete(self) -> bool: ...

    @property
    def size(self) -> Size:
        return self._sized.size

    @property
    def top_left(self) -> Coordinate:
        return self._sized.top_left

    @cached_property
    def _sized(self) -> SizableDrawingOnScreens:
        return SizableDrawingOnScreens(self.drawing_on_screens)


@dataclass(frozen=True)
class FromAnimation(AnimationOnScreen):
    coordinate: Coordinate
    animation: Animation

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.animation.drawing, Drawing):
            return (DrawingOnScreen(self.coordinate, self.animation.drawing),)
        return self.animation.drawing.drawing_on_screens(self.coordinate)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        animation = self.animation.tick(time_delta)
        return replace(self, animation=animation)

    @override
    @property
    def is_complete(self) -> bool:
        return self.animation.is_complete


_AnimationOnScreen = TypeVar("_AnimationOnScreen", bound=AnimationOnScreen)


def tick_optional(
    animation: _AnimationOnScreen | None, time_delta: Millisecond
) -> _AnimationOnScreen | None:
    if animation:
        return animation.tick(time_delta)
    return None
