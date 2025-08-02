from __future__ import annotations

from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import Self, override

from nextrpg.character.character_draw import CharacterDraw
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.core.dimension import Size
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
    _event_triggered: bool = False

    @property
    def display_name(self) -> str:
        return self.spec.display_name

    def tick(
        self, time_delta: Millisecond, others: tuple[CharacterOnScreen, ...]
    ) -> Self:
        return replace(self, character=self.character.tick_idle(time_delta))

    @property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        if self._collision_visual:
            return self.draw_on_screen, self._collision_visual
        return (self.draw_on_screen,)

    @cached_property
    def _collision_visual(self) -> DrawOnScreen | None:
        if config().debug and (
            color := config().debug.collision_rectangle_color
        ):
            return self.collision_rectangle.fill(color)
        return None

    @cached_property
    def collision_rectangle(self) -> RectangleOnScreen:
        return self._collision_rectangle(self.coordinate)

    def _collision_rectangle(self, coordinate: Coordinate) -> RectangleOnScreen:
        rect = DrawOnScreen(coordinate, self.character.draw).rectangle_on_screen
        width, height = rect.size
        rect_height = height * self.config.bounding_rectangle_height_percentage
        bounding_size = Size(width, rect_height)
        left, top = rect.top_left
        coord = Coordinate(left, top + (height - rect_height) / 2)
        return RectangleOnScreen(coord, bounding_size)

    @property
    def draw_on_screen(self) -> DrawOnScreen:
        return DrawOnScreen(self.coordinate, self.character.draw)

    def start_event(self, other: CharacterOnScreen) -> Self:
        direction = other.coordinate.relative_to(self.coordinate)
        turned_character = self.character.turn(direction)
        return replace(self, character=turned_character, _event_triggered=True)

    @property
    def complete_event(self) -> Self:
        return replace(self, _event_triggered=False)
