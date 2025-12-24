from collections.abc import Collection
from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import Any, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_spec import CharacterSpec
from nextrpg.character.polygon_character_drawing import PolygonCharacterDrawing
from nextrpg.character.view_only_character_drawing import (
    ViewOnlyCharacterDrawing,
)
from nextrpg.config.config import config
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.save import UpdateFromSave
from nextrpg.core.time import Millisecond
from nextrpg.drawing.color import TRANSPARENT
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import (
    DrawingOnScreens,
    drawing_on_screens,
)
from nextrpg.drawing.polygon_drawing import PolygonDrawing
from nextrpg.drawing.rectangle_drawing import RectangleDrawing
from nextrpg.drawing.sprite_on_screen import SpriteOnScreen
from nextrpg.event.event_as_attr import EventAsAttr
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polygon_area_on_screen import PolygonAreaOnScreen
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.geometry.scaling import WidthScaling
from nextrpg.geometry.size import Size


@dataclass_with_default(frozen=True)
class CharacterOnScreen(
    EventAsAttr, SpriteOnScreen, UpdateFromSave[dict[str, Any]]
):
    spec: CharacterSpec
    coordinate: Coordinate
    anchor: Anchor = Anchor.BOTTOM_CENTER
    _: KW_ONLY = private_init_below()
    character_drawing: CharacterDrawing = default(
        lambda self: self.spec.character_drawing
    )
    _event_started: bool = False

    @cached_property
    def transparent_drawing(self) -> Self:
        rect = (
            self.drawing_on_screen.rectangle_area_on_screen.rectangle_drawing(
                TRANSPARENT
            )
        )
        character_drawing = PolygonCharacterDrawing(rect_or_poly=rect)
        return self.with_character_drawing(character_drawing)

    def with_character_drawing(
        self, character_drawing: CharacterDrawing
    ) -> Self:
        return replace(self, character_drawing=character_drawing)

    @override
    @cached_property
    def top_left(self) -> Coordinate:
        return self.coordinate.as_anchor_of(self, self.anchor).top_left

    @override
    @cached_property
    def size(self) -> Size:
        return self.character_drawing.size

    @cached_property
    def name(self) -> str:
        return self.spec.display_name

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        return self.tick_with_others(time_delta, [])

    def tick_with_others(
        self, time_delta: Millisecond, others: Collection[CharacterOnScreen]
    ) -> Self:
        character_drawing = self.character_drawing.tick_idle(time_delta)
        return replace(self, character_drawing=character_drawing)

    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        character_drawing_on_screens = (
            self.character_drawing.drawing_on_screens(
                self.coordinate, self.anchor
            )
        )
        debug_visuals = drawing_on_screens(
            d
            for d in (self._collision_visual, self._start_event_visual)
            if d is not None
        )
        return character_drawing_on_screens + debug_visuals

    @cached_property
    def collision_rectangle_area_on_screen(self) -> AreaOnScreen:
        if self._area_on_screen:
            return self._area_on_screen
        return self._collision_rectangle_area_on_screen(self.coordinate)

    def has_same_name(self, other: CharacterOnScreen) -> bool:
        return self.spec.unique_name == other.spec.unique_name

    def start_event(self, other: CharacterOnScreen) -> Self:
        if isinstance(
            other.spec.character_drawing,
            PolygonCharacterDrawing | ViewOnlyCharacterDrawing,
        ):
            character_drawing = self.character_drawing
        else:
            direction = other.top_left.relative_to(self.top_left)
            character_drawing = self.character_drawing.turn(direction)
        return replace(
            self, character_drawing=character_drawing, _event_started=True
        )

    @cached_property
    def complete_event(self) -> Self:
        return replace(self, _event_started=False)

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return {
            "top_left": self.top_left.save_data,
            "character_drawing": self.character_drawing.save_data,
        }

    @override
    def update_this_class_from_save(self, data: dict[str, Any]) -> Self:
        top_left = Coordinate.load_from_save(data["top_left"])
        coordinate = top_left.as_top_left_of(self).at_anchor(self.anchor)
        character_drawing = self.character_drawing.update_from_save(
            data["character_drawing"]
        )
        return replace(
            self, coordinate=coordinate, character_drawing=character_drawing
        )

    @cached_property
    def _start_event_area_on_screen(self) -> AreaOnScreen:
        if self._area_on_screen:
            return self._area_on_screen

        scaling = self.spec.config.start_event_scaling
        top_left = self.top_left - self.width * (scaling - WidthScaling(1)) / 2
        size = self.size * scaling
        return top_left.as_top_left_of(size).rectangle_area_on_screen

    @cached_property
    def _area_on_screen(self) -> AreaOnScreen | None:
        if not isinstance(self.character_drawing, PolygonCharacterDrawing):
            return None

        match self.character_drawing.rect_or_poly:
            case RectangleDrawing() as rect:
                return self.top_left.as_top_left_of(
                    rect.size
                ).rectangle_area_on_screen
            case PolygonDrawing() as poly:
                points = tuple(p + self.top_left for p in poly.points)
                return PolygonAreaOnScreen(points)

    def _collision_rectangle_area_on_screen(
        self, coordinate: Coordinate
    ) -> RectangleAreaOnScreen:
        scaling = self.spec.config.bounding_rectangle_scaling
        size = self.size * scaling
        top_left = (
            coordinate.as_anchor_of(self, self.anchor).top_left
            + self.height * scaling.complement / 2
        )
        return top_left.as_top_left_of(size).rectangle_area_on_screen

    @cached_property
    def _collision_visual(self) -> DrawingOnScreen | None:
        if (debug := config().debug) and (color := debug.collision_rectangle):
            return self.collision_rectangle_area_on_screen.fill(color)
        return None

    @cached_property
    def _start_event_visual(self) -> DrawingOnScreen | None:
        if (debug := config().debug) and (color := debug.start_event_rectangle):
            return self._start_event_area_on_screen.fill(color)
        return None
