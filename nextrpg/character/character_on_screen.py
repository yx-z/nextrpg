from __future__ import annotations

from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self

from nextrpg.character.character_draw import CharacterDraw
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import Draw, DrawOnScreen, RectangleOnScreen
from nextrpg.draw.group import Group
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.global_config.character_config import CharacterConfig
from nextrpg.global_config.global_config import config


@dataclass_with_instance_init(frozen=True)
class CharacterSpec:
    object_name: str
    character: CharacterDraw
    avatar: Draw | Group | None = None
    display_name: str = instance_init(lambda self: self.object_name)


@dataclass_with_instance_init(frozen=True)
class CharacterOnScreen(EventAsAttr):
    spec: CharacterSpec
    coordinate: Coordinate
    config: CharacterConfig = field(default_factory=lambda: config().character)
    _: KW_ONLY = not_constructor_below()
    character: CharacterDraw = instance_init(lambda self: self.spec.character)
    _event_started: bool = False

    @property
    def display_name(self) -> str:
        return self.spec.display_name

    def tick(
        self, time_delta: Millisecond, others: tuple[CharacterOnScreen, ...]
    ) -> Self:
        return replace(self, character=self.character.tick_idle(time_delta))

    @property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        debug_visuals = tuple(
            d for d in (self._collision_visual, self._start_event_visual) if d
        )
        return (self.draw_on_screen,) + debug_visuals

    @cached_property
    def _collision_visual(self) -> DrawOnScreen | None:
        if config().debug and (
            color := config().debug.collision_rectangle_color
        ):
            return self.collision_rectangle.fill(color)
        return None

    @cached_property
    def _start_event_visual(self) -> DrawOnScreen | None:
        if config().debug and (
            color := config().debug.start_event_rectangle_color
        ):
            return self.start_event_rectangle.fill(color)
        return None

    @cached_property
    def collision_rectangle(self) -> RectangleOnScreen:
        return self._collision_rectangle(self.coordinate)

    @cached_property
    def start_event_rectangle(self) -> RectangleOnScreen:
        coord = self.coordinate - (
            self.draw_on_screen.width * (self.config.start_event_scaling - 1)
        )
        size = self.draw_on_screen.size * self.config.start_event_scaling
        return RectangleOnScreen(coord, size)

    def _collision_rectangle(self, coordinate: Coordinate) -> RectangleOnScreen:
        coord = (
            coordinate
            + self.draw_on_screen.height
            * self.config.bounding_rectangle_scaling
        )
        size = self.draw_on_screen.size * self.config.bounding_rectangle_scaling
        return RectangleOnScreen(coord, size)

    @property
    def draw_on_screen(self) -> DrawOnScreen:
        return DrawOnScreen(self.coordinate, self.character.draw)

    def start_event(self, other: CharacterOnScreen) -> Self:
        direction = other.coordinate.relative_to(self.coordinate)
        turned_character = self.character.turn(direction)
        return replace(self, character=turned_character, _event_started=True)

    @property
    def complete_event(self) -> Self:
        return replace(self, _event_started=False)
