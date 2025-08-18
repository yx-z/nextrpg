from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Literal, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import Size, WidthAndHeightScaling
from nextrpg.draw.drawing import (
    Drawing,
    DrawingOnScreen,
    PolygonOnScreen,
    RectangleDrawing,
    RectangleOnScreen,
)
from nextrpg.draw.drawing_group import (
    DrawingGroup,
    DrawingGroupOnScreen,
    RelativeDrawing,
)
from nextrpg.draw.text import Text, TextGroup
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.gui.area import gui_width, left_screen, top_screen
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class SayEventAddOn:
    config: SayEventConfig
    message: str | Text | TextGroup

    @cached_property
    def background(self) -> tuple[DrawingOnScreen, ...]:
        contents = [RelativeDrawing(self._text.drawing_group, ORIGIN)]
        if self._name_relative_to_text:
            contents.append(self._name_relative_to_text)
        if self._avatar_relative_to_text:
            contents.append(self._avatar_relative_to_text)
        content = DrawingGroup(tuple(contents))

        background, shift = self._background_relative_to_text
        add_on = DrawingGroup(
            (
                RelativeDrawing(background, ORIGIN),
                RelativeDrawing(content, -shift),
            )
        )
        add_on_on_screen = DrawingGroupOnScreen(self.add_on_top_left, add_on)

        text_coord = add_on_on_screen.coordinate(self._text.drawing_group)
        assert text_coord
        text_add_on = TextOnScreen(text_coord, self._text).drawing_on_screens
        return tuple(
            drawing_on_screen
            for drawing_on_screen in add_on_on_screen.drawing_on_screens
            if drawing_on_screen not in text_add_on
        )

    @cached_property
    def text_on_screen(self) -> TextOnScreen:
        coordinate = (
            self.add_on_top_left - self._background_relative_to_text.shift
        )
        return TextOnScreen(coordinate, self._text)

    @cached_property
    def add_on_top_left(self) -> Coordinate:
        return self._center_to_top_left(self.config.scene_coordinate)

    @property
    def avatar(self) -> Drawing | DrawingGroup | None:
        return self.config.avatar

    @property
    def name(self) -> str | None:
        if name := self.config.name_override:
            return name
        return None

    def _center_to_top_left(self, center: Coordinate) -> Coordinate:
        return (
            center
            - self._background_relative_to_text.drawing.size
            / WidthAndHeightScaling(2)
        )

    @cached_property
    def _background_relative_to_text(self) -> RelativeDrawing:
        shift = -self.config.padding
        size = self._text.size + self.config.padding * WidthAndHeightScaling(2)
        if self._name_relative_to_text:
            extra_height = (
                self._name_relative_to_text.drawing.height
                + self.config.padding.height
            )
            shift -= extra_height
            size += extra_height
        if self._avatar_relative_to_text:
            extra_width = (
                self._avatar_relative_to_text.drawing.size.width
                + self.config.padding.width
            )
            shift -= extra_width
            size += extra_width
        rect = RectangleDrawing(
            size, self.config.background, self.config.border_radius
        )
        return RelativeDrawing(rect, shift)

    @cached_property
    def _avatar_relative_to_text(self) -> RelativeDrawing | None:
        if not self.avatar:
            return None
        shift = (
            self._text.bottom_left
            - self.config.padding.width
            - self.avatar.size
        )
        return RelativeDrawing(self.avatar, shift.size)

    @cached_property
    def _name_relative_to_text(self) -> RelativeDrawing | None:
        if not self.name:
            return None
        text = Text(self.name, self.config.name_text_config)
        shift = Size(0, -text.height.value - self.config.padding.height.value)
        return RelativeDrawing(text.drawing_group, shift)

    @cached_property
    def _text(self) -> Text | TextGroup:
        if isinstance(self.message, str):
            return Text(self.message, self.config.text_config)
        return self.message


@dataclass(frozen=True)
class SayEventCharacterAddOn(SayEventAddOn):
    scene: Scene
    character: CharacterOnScreen

    @cached_property
    @override
    def background(self) -> tuple[DrawingOnScreen, ...]:
        return (self._background_tick,) + super().background

    @cached_property
    def _background_tick(self) -> DrawingOnScreen:
        if self._character_rectangle_on_screen.center in left_screen():
            width_sign = 1
        else:
            width_sign = -1
        height_sign = self._character_edge.height_sign
        character_left, character_top = self._character_edge.coordinate

        cfg = self.config.add_on
        tip_left = character_left + width_sign * cfg.tail_tip_shift.width
        tip_top = character_top + height_sign * cfg.tail_tip_shift.height

        base_coord1_left = tip_left + width_sign * cfg.tail_base1_shift
        base_coord2_left = tip_left + width_sign * cfg.tail_base2_shift

        base_coord_top = self.add_on_top_left
        if not self._character_edge.is_top:
            base_coord_top += self._background_relative_to_text.drawing.height

        tip_coord = Coordinate(tip_left.value, tip_top.value)
        base_coord1 = Coordinate(
            base_coord1_left.value, base_coord_top.top_value
        )
        base_coord2 = Coordinate(
            base_coord2_left.value, base_coord_top.top_value
        )
        tip = PolygonOnScreen((tip_coord, base_coord1, base_coord2))
        return tip.fill(self.config.background)

    @cached_property
    @override
    def add_on_top_left(self) -> Coordinate:
        if center := self.config.character_coordinate_override:
            return self._center_to_top_left(center)

        shift_width, shift_height = self.config.add_on.add_on_shift
        character_left, character_top = self._character_edge.coordinate
        center = character_left - shift_width

        # Clamp add-on within screen width.
        background_width = self._background_relative_to_text.drawing.width.value
        left = center - background_width / 2
        pad_width = self.config.padding.width.value
        if left < pad_width:
            left = pad_width
        elif left + background_width > gui_width() - pad_width:
            left = gui_width().value - background_width - pad_width

        top = character_top + self._character_edge.height_sign * shift_height
        if self._character_edge.is_top:
            top -= self._background_relative_to_text.drawing.height.value

        return Coordinate(left, top)

    @cached_property
    @override
    def avatar(self) -> Drawing | DrawingGroup | None:
        if self.config.avatar:
            return self.config.avatar
        return self.character.spec.avatar

    @cached_property
    @override
    def name(self) -> str:
        if self.config.name_override:
            return self.config.name_override
        return self.character.display_name

    @cached_property
    def _character_edge(self) -> _CharacterPosition:
        if self._character_rectangle_on_screen.center in top_screen():
            return _CharacterPosition(
                coordinate=self._character_rectangle_on_screen.bottom_center,
                is_top=True,
            )
        return _CharacterPosition(
            coordinate=self._character_rectangle_on_screen.top_center,
            is_top=False,
        )

    @cached_property
    def _character_rectangle_on_screen(self) -> RectangleOnScreen:
        rect = self.character.drawing_on_screen.visible_rectangle_on_screen
        if self.scene.drawing_on_screen_shift:
            return rect + self.scene.drawing_on_screen_shift
        return rect


@dataclass(frozen=True, kw_only=True)
class _CharacterPosition:
    coordinate: Coordinate
    is_top: bool

    @property
    def height_sign(self) -> Literal[-1, 1]:
        if self.is_top:
            return 1
        return -1
