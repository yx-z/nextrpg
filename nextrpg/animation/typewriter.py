from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Self, override

from nextrpg.animation.base_animation_on_screen import (
    BaseAnimationOnScreen,
)
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond, Timer
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.shifted_sprite import ShiftedSprite
from nextrpg.drawing.text_on_screen import TextOnScreen


@dataclass_with_default(frozen=True)
class Typewriter(BaseAnimationOnScreen):
    text_on_screen: TextOnScreen
    delay: Millisecond
    _: KW_ONLY = private_init_below()
    _index: int = 0
    _timer_per_character: Timer = default(lambda self: Timer(self.delay))

    @cached_property
    @override
    def drawing_on_screens(self) -> DrawingOnScreens:
        trimmed = self.text_on_screen.text[: self._index + 1]
        drawings: list[ShiftedSprite] = []
        for orig, trim in zip(
            self.text_on_screen.text.line_drawing_and_heights,
            trimmed.line_drawing_and_heights,
        ):
            height_diff = orig.height - trim.height
            drawings.append(trim.drawing + height_diff)
        drawing_group = DrawingGroup(tuple(drawings))
        return drawing_group.drawing_on_screens(self.text_on_screen.coordinate)

    @override
    def _tick_before_complete(self, time_delta: Millisecond) -> Self:
        if not (
            timer := self._timer_per_character.tick(time_delta)
        ).is_complete:
            return replace(self, _timer_per_character=timer)
        index = self._index + timer.elapsed // self.delay
        return replace(self, _index=index, _timer_per_character=timer.modulo)

    @override
    @cached_property
    def is_complete(self) -> bool:
        return self._index > len(self.text_on_screen.text)
