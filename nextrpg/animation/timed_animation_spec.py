from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import Any, Self

from frozendict import frozendict

from nextrpg.animation.animation_spec import AnimationSpec
from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.config.config import config
from nextrpg.core.time import Millisecond
from nextrpg.drawing.shifted_sprite import ShiftedSprite
from nextrpg.drawing.sprite import Sprite
from nextrpg.drawing.sprite_on_screen import SpriteOnScreen, animate_on_screen
from nextrpg.geometry.anchor import Anchor


@dataclass(frozen=True)
class TimedAnimationSpec(AnimationSpec):
    cls: type[TimedAnimationGroup]
    duration: Millisecond = field(
        default_factory=lambda: config().animation.default_timed_animation_duration
    )
    reverse: bool = False
    others: tuple[_TimedAnimationGroupTypeAndKwargs, ...] = ()

    def compose(self, cls: type[TimedAnimationGroup], **kwargs: Any) -> Self:
        spec = _TimedAnimationGroupTypeAndKwargs(cls, frozendict(kwargs))
        others = self.others + (spec,)
        return replace(self, others=others)

    def animate(
        self,
        resource: Sprite | ShiftedSprite | tuple[Sprite | ShiftedSprite, ...],
    ) -> TimedAnimationGroup:
        res = self.cls(resource, self.duration, **self.kwargs)
        for o in self.others:
            res = res.compose(o.cls, **o.kwargs)
        if self.reverse:
            return res.reversed
        return res

    @cached_property
    def reversed(self) -> Self:
        reverse = not self.reverse
        return replace(self, reverse=reverse)

    def animate_on_screen(
        self,
        resource: SpriteOnScreen | tuple[SpriteOnScreen, ...],
        anchor: Anchor = Anchor.TOP_LEFT,
    ) -> TimedAnimationOnScreens:
        res = animate_on_screen(resource, self.cls, anchor, **self.kwargs)
        for o in self.others:
            res = res.compose(o.cls, **o.kwargs)
        if self.reverse:
            return res.reversed
        return res


@dataclass(frozen=True)
class _TimedAnimationGroupTypeAndKwargs:
    cls: type[TimedAnimationGroup]
    kwargs: frozendict[str, Any]
