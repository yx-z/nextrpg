from dataclasses import dataclass
from typing import Any

from frozendict import frozendict

from nextrpg.animation.animation_group import AnimationGroup
from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.drawing.shifted_sprite import ShiftedSprite
from nextrpg.drawing.sprite import Sprite
from nextrpg.drawing.sprite_on_screen import SpriteOnScreen, animate_on_screen
from nextrpg.geometry.anchor import Anchor


@dataclass(frozen=True)
class AnimationSpec:
    cls: type[AnimationGroup]
    kwargs: frozendict[str, Any] = frozendict()

    def animate(
        self,
        resource: Sprite | ShiftedSprite | tuple[Sprite | ShiftedSprite, ...],
    ) -> AnimationGroup:
        return self.cls(resource, **self.kwargs)

    def animate_on_screen(
        self,
        resource: SpriteOnScreen | tuple[SpriteOnScreen, ...],
        anchor: Anchor = Anchor.TOP_LEFT,
    ) -> AnimationOnScreens:
        res = animate_on_screen(resource, self.cls, anchor, **self.kwargs)
