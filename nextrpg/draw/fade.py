from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.core.color import alpha_from_percentage
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.draw.animation_on_screen import AnimationOnScreen
from nextrpg.draw.drawing import DrawingOnScreen
from nextrpg.global_config.global_config import config


@dataclass_with_init(frozen=True)
class _Fade(AnimationOnScreen, ABC):
    drawing_on_screen: DrawingOnScreen | tuple[DrawingOnScreen, ...]
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
        return replace(self, _timer=timer)

    @property
    def complete(self) -> bool:
        return self._timer.complete

    @cached_property
    def _drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if isinstance(self.drawing_on_screen, DrawingOnScreen):
            return (self.drawing_on_screen,)
        return self.drawing_on_screen

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
