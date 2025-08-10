from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Self

from nextrpg.character.character_draw import CharacterDraw
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.dimension import Size
from nextrpg.core.sizeable import Sizeable
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import Draw, DrawOnScreen, RectangleOnScreen
from nextrpg.draw.group import Group
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.global_config.character_config import CharacterConfig
from nextrpg.global_config.global_config import config


@dataclass_with_init(frozen=True)
class _BaseCharacterSpec:
    object_name: str
    obstruct_others: bool = True
    collide_with_others: bool = True
    avatar: Draw | Group | None = None
    display_name: str = default(lambda self: self.object_name)
    config: CharacterConfig = field(default_factory=lambda: config().character)


@dataclass(frozen=True, kw_only=True)
class CharacterSpec(_BaseCharacterSpec):
    character: CharacterDraw


@dataclass_with_init(frozen=True)
class CharacterOnScreen(EventAsAttr, Sizeable):
    spec: CharacterSpec
    coordinate: Coordinate
    config: CharacterConfig = field(default_factory=lambda: config().character)
    _: KW_ONLY = not_constructor_below()
    character: CharacterDraw = default(lambda self: self.spec.character)
    _event_started: bool = False

    @property
    def top_left(self) -> Coordinate:
        return self.coordinate

    @property
    def size(self) -> Size:
        return self.draw_on_screen.size

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
        if (
            (debug := config().debug)
            and (color := debug.collision_rectangle_color)
            and self.collision_rectangle
        ):
            return self.collision_rectangle.fill(color)
        return None

    @cached_property
    def _start_event_visual(self) -> DrawOnScreen | None:
        if (
            (debug := config().debug)
            and (color := debug.start_event_rectangle_color)
            and self.start_event_rectangle
        ):
            return self.start_event_rectangle.fill(color)
        return None

    @cached_property
    def collision_rectangle(self) -> RectangleOnScreen | None:
        if self.spec.obstruct_others:
            return self._collision_rectangle(self.coordinate)
        return None

    @cached_property
    def start_event_rectangle(self) -> RectangleOnScreen | None:
        scaling = self.config.start_event_scaling
        coord = self.coordinate - self.width * (scaling - 1) / 2
        size = self.size * scaling
        return RectangleOnScreen(coord, size)

    def _collision_rectangle(self, coordinate: Coordinate) -> RectangleOnScreen:
        scaling = self.config.bounding_rectangle_scaling
        coord = coordinate + self.height * (1 - scaling) / 2
        size = self.size * scaling
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
