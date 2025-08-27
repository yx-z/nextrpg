from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import Any, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.dimension import Size
from nextrpg.core.direction import Direction
from nextrpg.core.save import UpdateFromSave
from nextrpg.core.sizable import Sizable
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.global_config.character_config import CharacterConfig
from nextrpg.global_config.global_config import config


@dataclass_with_init(frozen=True)
class _BaseCharacterSpec:
    unique_name: str
    collide_with_others: bool = True
    avatar: Drawing | DrawingGroup | None = None
    display_name: str = default(lambda self: self.unique_name)
    config: CharacterConfig = field(default_factory=lambda: config().character)


@dataclass(frozen=True, kw_only=True)
class CharacterSpec(_BaseCharacterSpec):
    character: CharacterDrawing


@dataclass_with_init(frozen=True)
class CharacterOnScreen(EventAsAttr, Sizable, UpdateFromSave):
    spec: CharacterSpec
    coordinate: Coordinate
    config: CharacterConfig = field(default_factory=lambda: config().character)
    _: KW_ONLY = not_constructor_below()
    character: CharacterDrawing = default(lambda self: self.spec.character)
    _event_started: bool = False

    @property
    def top_left(self) -> Coordinate:
        return self.coordinate

    @property
    def size(self) -> Size:
        return self.drawing_on_screen.size

    @property
    def display_name(self) -> str:
        return self.spec.display_name

    def tick(
        self, time_delta: Millisecond, others: tuple[CharacterOnScreen, ...]
    ) -> Self:
        return replace(self, character=self.character.tick_idle(time_delta))

    @property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        debug_visuals = tuple(
            d for d in (self._collision_visual, self._start_event_visual) if d
        )
        return (self.drawing_on_screen,) + debug_visuals

    @cached_property
    def collision_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        return self._collision_rectangle_area_on_screen(self.coordinate)

    @cached_property
    def start_event_rectangle_area_on_screen(self) -> RectangleAreaOnScreen:
        scaling = self.config.start_event_scaling
        coordinate = self.coordinate - self.width * (scaling - 1) / 2
        size = self.size * scaling
        return RectangleAreaOnScreen(coordinate, size)

    @property
    def drawing_on_screen(self) -> DrawingOnScreen:
        return DrawingOnScreen(self.coordinate, self.character.drawing)

    def same_name(self, other: CharacterOnScreen) -> bool:
        return self.spec.unique_name == other.spec.unique_name

    def start_event(self, other: CharacterOnScreen, turn: bool) -> Self:
        if turn:
            direction = other.coordinate.relative_to(self.coordinate)
            character = self.character.turn(direction)
        else:
            character = self.character
        return replace(self, character=character, _event_started=True)

    @property
    def complete_event(self) -> Self:
        return replace(self, _event_started=False)

    @override
    @property
    def key(self) -> tuple[str, ...]:
        return super().key + (self.spec.unique_name,)

    @override
    @property
    def save_data(self) -> dict[str, Any]:
        return {
            "coordinate": self.coordinate.save_data,
            "direction": self.character.direction.save_data,
        }

    @override
    def update(self, save: dict[str, Any]) -> Self:
        coordinate = Coordinate.load(save["coordinate"])
        direction = Direction.load(save["direction"])
        character = self.character.turn(direction)
        return replace(self, coordinate=coordinate, character=character)

    def _collision_rectangle_area_on_screen(
        self, coordinate: Coordinate
    ) -> RectangleAreaOnScreen:
        scaling = self.config.bounding_rectangle_scaling
        coordinate = coordinate + self.height * (1 - scaling) / 2
        size = self.size * scaling
        return RectangleAreaOnScreen(coordinate, size)

    @cached_property
    def _collision_visual(self) -> DrawingOnScreen | None:
        if (debug := config().debug) and (
            color := debug.collision_rectangle_color
        ):
            return self.collision_rectangle_area_on_screen.fill(color)
        return None

    @cached_property
    def _start_event_visual(self) -> DrawingOnScreen | None:
        if (debug := config().debug) and (
            color := debug.start_event_rectangle_color
        ):
            return self.start_event_rectangle_area_on_screen.fill(color)
        return None
