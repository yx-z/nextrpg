from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self, override

from nextrpg.core.save import UpdateFromSave
from nextrpg.core.time import Millisecond
from nextrpg.drawing.sprite import Sprite
from nextrpg.geometry.direction import Direction


@dataclass(frozen=True)
class CharacterDrawing(Sprite, UpdateFromSave):
    direction: Direction = Direction.DOWN

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return {"direction": self.direction.save_data}

    @override
    def update_this_class_from_save(self, data: dict[str, Any]) -> Self | None:
        direction_str = data["direction"]
        direction = Direction.load_from_save(direction_str)
        return replace(self, direction=direction)

    def turn(self, direction: Direction) -> Self:
        return self

    def tick_idle(self, time_delta: Millisecond) -> Self:
        return self

    def tick_action(self, time_delta: Millisecond, action: Any) -> Self:
        return self
