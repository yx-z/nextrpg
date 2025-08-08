from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Literal, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import Size, WidthAndHeightScaling
from nextrpg.draw.draw import (
    Draw,
    DrawOnScreen,
    PolygonOnScreen,
    RectangleDraw,
    RectangleOnScreen,
)
from nextrpg.draw.group import Group, GroupOnScreen, RelativeDraw
from nextrpg.draw.text import Text, TextGroup
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.gui.area import gui_width, left_screen, top_screen
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class AddOn:
    config: SayEventConfig
    message: str | Text | TextGroup

    @cached_property
    def background(self) -> tuple[DrawOnScreen, ...]:
        contents = [RelativeDraw(self._text.group, ORIGIN)]
        if self._name_relative_to_text:
            contents.append(self._name_relative_to_text)
        if self._avatar_relative_to_text:
            contents.append(self._avatar_relative_to_text)
        content = Group(tuple(contents))

        background, shift = self._background_relative_to_text
        add_on = Group(
            (RelativeDraw(background, ORIGIN), RelativeDraw(content, -shift))
        )
        add_on_on_screen = GroupOnScreen(self.add_on_top_left, add_on)

        text_coord = add_on_on_screen.coordinate(self._text.group)
        text_add_on = TextOnScreen(text_coord, self._text).draw_on_screens
        return tuple(
            d for d in add_on_on_screen.draw_on_screens if d not in text_add_on
        )

    @cached_property
    def text_on_screen(self) -> TextOnScreen:
        coord = self.add_on_top_left - self._background_relative_to_text.shift
        return TextOnScreen(coord, self._text)

    @cached_property
    def add_on_top_left(self) -> Coordinate:
        return self._center_to_top_left(self.config.scene_coordinate)

    def _center_to_top_left(self, center: Coordinate) -> Coordinate:
        return (
            center
            - self._background_relative_to_text.draw.size
            / WidthAndHeightScaling(2)
        )

    @cached_property
    def _background_relative_to_text(self) -> RelativeDraw:
        shift = -self.config.padding
        size = self._text.size + self.config.padding * WidthAndHeightScaling(2)
        if self._name_relative_to_text:
            extra_height = (
                self._name_relative_to_text.draw.height
                + self.config.padding.height
            )
            shift -= extra_height
            size += extra_height
        if self._avatar_relative_to_text:
            extra_width = (
                self._avatar_relative_to_text.draw.size.width
                + self.config.padding.width
            )
            shift -= extra_width
            size += extra_width
        rect = RectangleDraw(
            size, self.config.background, self.config.border_radius
        )
        return RelativeDraw(rect, shift)

    @property
    def _avatar(self) -> Draw | Group | None:
        return self.config.avatar

    @cached_property
    def _avatar_relative_to_text(self) -> RelativeDraw | None:
        if not self._avatar:
            return None
        shift = (
            self._text.bottom_left
            - self.config.padding.width
            - self._avatar.size
        )
        return RelativeDraw(self._avatar, shift.size)

    @property
    def _name(self) -> str | None:
        if name := self.config.name_override:
            return name
        return None

    @cached_property
    def _name_relative_to_text(self) -> RelativeDraw | None:
        if not self._name:
            return None
        text = Text(self._name, self.config.name_text_config)
        shift = Size(0, -text.height - self.config.padding.height)
        return RelativeDraw(text.group, shift)

    @cached_property
    def _text(self) -> Text | TextGroup:
        if isinstance(self.message, str):
            return Text(self.message, self.config.text_config)
        return self.message


@dataclass(frozen=True)
class CharacterAddOn(AddOn):
    scene: Scene
    character: CharacterOnScreen

    @cached_property
    @override
    def background(self) -> tuple[DrawOnScreen, ...]:
        return (self._background_tick,) + super().background

    @cached_property
    def _background_tick(self) -> DrawOnScreen:
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

        base_coord_top = self.add_on_top_left.top
        if not self._character_edge.is_top:
            base_coord_top += self._background_relative_to_text.draw.height

        tip_coord = Coordinate(tip_left, tip_top)
        base_coord1 = Coordinate(base_coord1_left, base_coord_top)
        base_coord2 = Coordinate(base_coord2_left, base_coord_top)
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
        background_width = self._background_relative_to_text.draw.width
        left = center - background_width / 2
        pad_width = self.config.padding.width
        if left < pad_width:
            left = pad_width
        elif left + background_width > gui_width() - pad_width:
            left = gui_width() - background_width - pad_width

        top = character_top + self._character_edge.height_sign * shift_height
        if self._character_edge.is_top:
            top -= self._background_relative_to_text.draw.height

        return Coordinate(left, top)

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
        rect = self.character.draw_on_screen.visible_rectangle_on_screen
        if self.scene.draw_on_screen_shift:
            return rect + self.scene.draw_on_screen_shift
        return rect

    @cached_property
    @override
    def _avatar(self) -> Draw | Group | None:
        if self.config.avatar:
            return self.config.avatar
        return self.character.spec.avatar

    @cached_property
    @override
    def _name(self) -> str:
        if self.config.name_override:
            return self.config.name_override
        return self.character.display_name


@dataclass(frozen=True, kw_only=True)
class _CharacterPosition:
    coordinate: Coordinate
    is_top: bool

    @property
    def height_sign(self) -> Literal[-1, 1]:
        if self.is_top:
            return 1
        return -1
