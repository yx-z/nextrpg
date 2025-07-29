from dataclasses import KW_ONLY, replace
from typing import Self, override

from nextrpg.draw.group import Group
from nextrpg.character.character_draw import CharacterDraw
from nextrpg.core.coordinate import Coordinate, Moving
from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.animated_on_screen import AnimatedOnScreen
from nextrpg.draw.draw import Draw, DrawOnScreen
from nextrpg.event.event_as_attr import EventAsAttr


@dataclass_with_instance_init(frozen=True)
class CharacterSpec:
    object_name: str
    character: CharacterDraw
    avatar: Draw | Group | None = None
    display_name: str = instance_init(lambda self: self.object_name)


@dataclass_with_instance_init(frozen=True, kw_only=True)
class CharacterOnScreen(EventAsAttr, Moving, AnimatedOnScreen):
    spec: CharacterSpec
    coordinate: Coordinate
    _: KW_ONLY = not_constructor_below()
    character: CharacterDraw = instance_init(lambda self: self.spec.character)
    _event_triggered: bool = False

    @property
    def display_name(self) -> str:
        return self.spec.display_name

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return replace(self, character=self.character.tick_idle(time_delta))

    @property
    @override
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        # TODO: Add visuals.
        return (self.draw_on_screen,)

    @property
    def draw_on_screen(self) -> DrawOnScreen:
        return DrawOnScreen(self.coordinate, self.character.draw)

    def start_event(self, character: Self) -> Self:
        direction = character.coordinate.relative_to(self.coordinate)
        turned_character = self.character.turn(direction)
        return replace(self, character=turned_character, _event_triggered=True)

    @property
    def complete_event(self) -> Self:
        return replace(self, _event_triggered=False)
