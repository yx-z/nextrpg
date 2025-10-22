from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Any, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_spec import CharacterSpec
from nextrpg.character.polygon_character_drawing import PolygonCharacterDrawing
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.save import UpdateFromSave, concat_save_key
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size, WidthScaling
from nextrpg.geometry.direction import Direction
from nextrpg.geometry.polygon_area_on_screen import PolygonAreaOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen


@dataclass_with_default(frozen=True)
class CharacterOnScreen(EventAsAttr, AnimationOnScreenLike, UpdateFromSave):
    spec: CharacterSpec
    coordinate: Coordinate
    _: KW_ONLY = private_init_below()
    character: CharacterDrawing = default(lambda self: self.spec.character)
    _event_started: bool = False

    @override
    @cached_property
    def top_left(self) -> Coordinate:
        return self.coordinate

    @override
    @cached_property
    def size(self) -> Size:
        return self.character.size

    @cached_property
    def name(self) -> str:
        return self.spec.display_name

    @override
    def tick(
        self, time_delta: Millisecond, others: tuple[CharacterOnScreen, ...]
    ) -> Self:
        return replace(self, character=self.character.tick_idle(time_delta))

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        character_drawing_on_screens = self.character.drawing_on_screens(
            self.coordinate
        )
        debug_visuals = tuple(
            d
            for d in (self._collision_visual, self._start_event_visual)
            if d is not None
        )
        return character_drawing_on_screens + debug_visuals

    @cached_property
    def collision_rectangle_area_on_screen(self) -> AreaOnScreen:
        if self._area_on_screen is not None:
            return self._area_on_screen
        return self._collision_rectangle_area_on_screen(self.coordinate)

    def is_same_name(self, other: CharacterOnScreen) -> bool:
        return self.spec.unique_name == other.spec.unique_name

    def start_event(self, other: CharacterOnScreen) -> Self:
        if isinstance(other.spec.character, PolygonCharacterDrawing):
            character = self.character
        else:
            direction = other.coordinate.relative_to(self.coordinate)
            character = self.character.turn(direction)
        return replace(self, character=character, _event_started=True)

    @cached_property
    def complete_event(self) -> Self:
        return replace(self, _event_started=False)

    @override
    @cached_property
    def save_key(self) -> str:
        return concat_save_key(super().save_key, self.spec.unique_name)

    @override
    @cached_property
    def save_data(self) -> dict[str, Any]:
        return {
            Coordinate.save_key(): self.coordinate.save_data,
            Direction.save_key(): self.character.direction.save_data,
        }

    @override
    def update_from_save(self, data: dict[str, Any]) -> Self:
        coordinate_data = data[Coordinate.save_key()]
        coordinate = Coordinate.load_from_save(coordinate_data)

        direction_data = data[Direction.save_key()]
        direction = Direction.load_from_save(direction_data)

        character = self.character.turn(direction)
        return replace(self, coordinate=coordinate, character=character)

    @cached_property
    def _start_event_area_on_screen(self) -> AreaOnScreen:
        if self._area_on_screen:
            return self._area_on_screen

        scaling = self.spec.config.start_event_scaling
        coordinate = (
            self.coordinate - self.width * (scaling - WidthScaling(1)) / 2
        )
        size = self.size * scaling
        return coordinate.anchor(size).rectangle_area_on_screen

    @cached_property
    def _area_on_screen(self) -> AreaOnScreen | None:
        if not isinstance(self.character, PolygonCharacterDrawing):
            return None

        match self.character.rect_or_poly:
            case RectangleDrawing() as rect:
                return self.coordinate.anchor(
                    rect.size
                ).rectangle_area_on_screen
            case PolygonDrawing() as poly:
                points = tuple(p + self.coordinate for p in poly.points)
                return PolygonAreaOnScreen(points)

    def _collision_rectangle_area_on_screen(
        self, coordinate: Coordinate
    ) -> RectangleAreaOnScreen:
        scaling = self.spec.config.bounding_rectangle_scaling
        coordinate = coordinate + self.height * scaling.complement / 2
        size = self.size * scaling
        return coordinate.anchor(size).rectangle_area_on_screen

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
            return self._start_event_area_on_screen.fill(color)
        return None
