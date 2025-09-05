from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.color import alpha_from_percentage
from nextrpg.draw.drawing_on_screen import DrawingOnScreen


@dataclass_with_default(frozen=True)
class Fade(AnimationOnScreen, ABC):
    resource: (
        AnimationOnScreen
        | DrawingOnScreen
        | tuple[DrawingOnScreen | AnimationOnScreen, ...]
    )
    duration: Millisecond = field(
        default_factory=lambda: config().timing.fade_duration
    )
    _: KW_ONLY = private_init_below()
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
        match self.resource:
            case AnimationOnScreen():
                resource = self.resource.tick(time_delta)
            case tuple():
                resource = tuple(
                    (
                        resource.tick(time_delta)
                        if isinstance(resource, AnimationOnScreen)
                        else resource
                    )
                    for resource in self.resource
                )
            case _:
                resource = self.resource
        timer = self._timer.tick(time_delta)
        return replace(self, resource=resource, _timer=timer)

    @override
    @property
    def complete(self) -> bool:
        return self._timer.complete

    @cached_property
    def _drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.resource, AnimationOnScreen):
            return self.resource.drawing_on_screens
        if isinstance(self.resource, DrawingOnScreen):
            return (self.resource,)
        res: list[DrawingOnScreen] = []
        for resource in self.resource:
            if isinstance(resource, AnimationOnScreen):
                res += resource.drawing_on_screens
            else:
                res.append(resource)
        return tuple(res)

    @property
    @abstractmethod
    def _start(self) -> tuple[DrawingOnScreen, ...]: ...

    @property
    @abstractmethod
    def _complete(self) -> tuple[DrawingOnScreen, ...]: ...

    @property
    @abstractmethod
    def _percentage(self) -> float: ...


class FadeIn(Fade):
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


class FadeOut(Fade):
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
