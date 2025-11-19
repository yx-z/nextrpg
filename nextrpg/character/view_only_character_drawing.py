from dataclasses import dataclass, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing import Drawing
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.sprite import Sprite
from nextrpg.geometry.direction import Direction


@dataclass(frozen=True, kw_only=True)
class ViewOnlyCharacterDrawing(CharacterDrawing):
    resource: Sprite

    @cached_property
    def drawing(self) -> Drawing | DrawingGroup:
        return self.resource.drawing

    @override
    def turn(self, direction: Direction) -> Self:
        return self

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        resource = self.resource.tick(time_delta)
        return replace(self, resource=resource)

    @override
    def tick_idle(self, time_delta: Millisecond) -> Self:
        return self.tick(time_delta)

    @override
    def tick_action(self, time_delta: Millisecond, action: Any) -> Self:
        return self.tick(time_delta)
