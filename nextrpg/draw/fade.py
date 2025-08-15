from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self, TypeIs, override

from nextrpg.core.color import alpha_from_percentage
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.animated_on_screen import AnimatedOnScreen
from nextrpg.draw.drawing import DrawingOnScreen
from nextrpg.global_config.global_config import config

type Resource = (
    DrawingOnScreen
    | tuple[DrawingOnScreen, ...]
    | AnimatedOnScreen
    | tuple[AnimatedOnScreen, ...]
)


@dataclass_with_init(frozen=True)
class _Fade(AnimatedOnScreen, ABC):
    resource: Resource
    duration: Millisecond = field(
        default_factory=lambda: config().transition.duration
    )
    _: KW_ONLY = not_constructor_below()
    _timer: Timer = default(lambda self: Timer(self.duration))

    @cached_property
    @override
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self._timer.complete:
            return self._complete
        if self._timer.elapsed == 0:
            return self._start

        alpha = alpha_from_percentage(self._percentage)
        return tuple(d.set_alpha(alpha) for d in self._drawing_on_screens)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        timer = self._timer.tick(time_delta)
        if isinstance(self.resource, AnimatedOnScreen):
            animation = self.resource.tick(time_delta)
            return replace(self, resource=animation, _timer=timer)
        if _is_animated_tuple(self.resource):
            animations = tuple(a.tick(time_delta) for a in self.resource)
            return replace(self, resource=animations, _timer=timer)
        return replace(self, _timer=timer)

    @property
    def complete(self) -> bool:
        return self._timer.complete

    @cached_property
    def _drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.resource, DrawingOnScreen):
            return (self.resource,)
        if isinstance(self.resource, AnimatedOnScreen):
            return self.resource.drawing_on_screens
        if _is_animated_tuple(self.resource):
            return tuple(d for a in self.resource for d in a.drawing_on_screens)
        return self.resource

    @property
    @abstractmethod
    def _start(self) -> tuple[DrawingOnScreen, ...]: ...

    @property
    @abstractmethod
    def _complete(self) -> tuple[DrawingOnScreen, ...]: ...

    @property
    @abstractmethod
    def _percentage(self) -> float: ...


class FadeIn(_Fade):
    @override
    @property
    def _start(self) -> tuple[DrawingOnScreen, ...]:
        return ()

    @override
    @property
    def _complete(self) -> tuple[DrawingOnScreen, ...]:
        return self._drawing_on_screens

    @override
    @property
    def _percentage(self) -> float:
        return self._timer.completed_percentage


class FadeOut(_Fade):
    @override
    @property
    def _percentage(self) -> float:
        return self._timer.remaining_percentage

    @override
    @property
    def _start(self) -> tuple[DrawingOnScreen, ...]:
        return self._drawing_on_screens

    @override
    @property
    def _complete(self) -> tuple[DrawingOnScreen, ...]:
        return ()


def _is_animated_tuple(
    resource: Resource,
) -> TypeIs[tuple[AnimatedOnScreen, ...]]:
    if not resource:
        return False
    if not isinstance(resource, tuple):
        return False
    if not isinstance(resource[0], AnimatedOnScreen):
        return False
    return True
