from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import Any, Self

from nextrpg.animation.timed_animation_group import TimedAnimationGroup
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.drawing.animation_on_screen_like import (
    AnimationOnScreenLike,
    animate,
)
from nextrpg.geometry.anchor import Anchor


@dataclass(frozen=True)
class TimedAnimationSpec:
    _: KW_ONLY = private_init_below()
    animations: tuple[tuple[type[TimedAnimationGroup], dict[str, Any]], ...]
    anchor: Anchor
    is_reversed: bool

    @cached_property
    def reverse(self) -> Self:
        return replace(self, is_reversed=not self.is_reversed)

    def __init__(
        self,
        animation_type: type[TimedAnimationGroup] | None = None,
        animations: tuple[
            tuple[type[TimedAnimationGroup], dict[str, Any]], ...
        ] = (),
        anchor: Anchor = Anchor.TOP_LEFT,
        is_reversed: bool = False,
        **kwargs: Any,
    ) -> None:
        if animation_type:
            animations += ((animation_type, kwargs),)
        object.__setattr__(self, "anchor", anchor)
        object.__setattr__(self, "animations", animations)
        object.__setattr__(self, "is_reversed", is_reversed)

    def compose(
        self, animation_type: type[TimedAnimationGroup], **kwargs: Any
    ) -> Self:
        animations = self.animations + ((animation_type, kwargs),)
        return replace(self, animations=animations)

    def animate(
        self,
        resource: AnimationOnScreenLike | tuple[AnimationOnScreenLike, ...],
    ) -> TimedAnimationOnScreens:
        animation_type, kwargs = self.animations[0]
        animation = animate(resource, animation_type, self.anchor, **kwargs)
        for animation_type, kwargs in self.animations[1:]:
            animation = animation.compose(animation_type, **kwargs)
        if self.is_reversed:
            return animation.reverse
        return animation
