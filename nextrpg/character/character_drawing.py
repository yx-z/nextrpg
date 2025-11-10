from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self, override

from nextrpg.core.module_and_attribute import ModuleAndAttribute
from nextrpg.core.save import UpdateFromSave
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.geometry.direction import Direction


@dataclass(frozen=True)
class CharacterDrawing(AnimationLike, UpdateFromSave):
    direction: Direction = Direction.DOWN
    update_function: (
        ModuleAndAttribute[
            Callable[[CharacterDrawing, dict[str, Any]], CharacterDrawing]
        ]
        | None
    ) = None

    @override
    @cached_property
    def save_data(self) -> dict[str, Any]:
        if self.update_function:
            update_function = self.update_function.save_data
        else:
            update_function = None
        return {
            "direction": self.direction.save_data,
            "update": update_function,
        }

    @override
    def update_from_save(self, data: dict[str, Any]) -> Self | None:
        if update := data.get("update"):
            init = ModuleAndAttribute.load_from_save(update)
            return init.imported(self, data)
        direction = Direction.load_from_save(data["direction"])
        return replace(self, direction=direction)

    def turn(self, direction: Direction) -> Self:
        return self

    def tick_idle(self, time_delta: Millisecond) -> Self:
        return self

    def tick_action(self, time_delta: Millisecond, action: Any) -> Self:
        return self
