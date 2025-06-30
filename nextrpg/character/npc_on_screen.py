from dataclasses import dataclass, field
from functools import cached_property
from typing import override

from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    MovingCharacterOnScreen,
)
from nextrpg.config import config
from nextrpg.core import Millisecond
from nextrpg.draw_on_screen import Polygon


@dataclass
class StaticNpcOnScreen(CharacterOnScreen):
    pass


@dataclass
class MovingNpcOnScreen(MovingCharacterOnScreen):
    path: Polygon = field()
    idle_duration: Millisecond = field(
        default_factory=lambda: config().character.idle_duration
    )

    @cached_property
    @override
    def is_moving(self) -> bool:
        return True

    @override
    def move(self, time_delta: Millisecond) -> Coordinate:
        return self.coordinate
