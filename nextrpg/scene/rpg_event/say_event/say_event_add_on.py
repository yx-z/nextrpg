from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Literal, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import ORIGIN, Coordinate
from nextrpg.core.dimension import Size, WidthAndHeightScaling
from nextrpg.core.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.rectangle_drawing import RectangleDrawing
from nextrpg.draw.relative_drawing import RelativeDrawing
from nextrpg.draw.text import Text
from nextrpg.draw.text_group import TextGroup
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.global_config.say_event_config import (
    SayEventConfig,
    SayEventNineSliceBackgroundConfig,
)
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

        background = self._background_relative_to_text.drawing
        shift = self._background_relative_to_text.shift
        background_and_content = (
            RelativeDrawing(background, ORIGIN),
            RelativeDrawing(content, -shift),
        )
        add_on_group = DrawingGroup(background_and_content)
        drawing_on_screens = add_on_group.drawing_on_screens(
            self._background_top_left
        )
        return tuple(
            drawing_on_screen
            for drawing_on_screen in drawing_on_screens
            if drawing_on_screen.drawing not in self._text.drawings
        )

    @cached_property
    def text_on_screen(self) -> TextOnScreen:
        coordinate = (
            self._background_top_left - self._background_relative_to_text.shift
        )
        return TextOnScreen(coordinate, self._text)

    @cached_property
    def _background_top_left(self) -> Coordinate:
        return self.config.scene_coordinate.as_center_of(
            self._background_relative_to_text.drawing
        ).top_left

    @property
    def _avatar(self) -> Drawing | DrawingGroup | None:
        return self.config.avatar

    @property
    def _name(self) -> str | None:
        return self.config.name_override

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

        if isinstance(
            cfg := self.config.background, SayEventNineSliceBackgroundConfig
        ):
            rect = cfg.nine_slice.stretch(size)
        else:
            rect = RectangleDrawing(
                size, cfg.background, cfg.border_radius
            ).drawing
        return RelativeDrawing(rect, shift)

    @cached_property
    def _avatar_relative_to_text(self) -> RelativeDrawing | None:
        if not self._avatar:
            return None
        shift = (
            self._text.bottom_left
            - self.config.padding.width
            - self._avatar.size
        )
        return RelativeDrawing(self._avatar, shift.size)

    @cached_property
    def _name_relative_to_text(self) -> RelativeDrawing | None:
        if not self._name:
            return None
        text = Text(self._name, self.config.name_text_config)
        shift = -(text.height + self.config.padding.height).with_width(0)
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
    def _background_relative_to_text(self) -> RelativeDrawing:
        relative = super()._background_relative_to_text
        if not self._tip:
            return relative

        background_drawing = relative.drawing
        if self._character_position.at_top:
            tip_top = -self._tip.height.value
        else:
            tip_top = background_drawing.height.value
        tip_left = (
            background_drawing.width.value / 2
            + self._width_sign * self.config.background_edge_center_to_tip.value
        )
        if not self._character_position.at_left:
            tip_left -= self._tip.width.value

        tip_shift = Size(tip_left, tip_top)
        background_and_tip = (
            RelativeDrawing(background_drawing, ORIGIN),
            RelativeDrawing(self._tip, tip_shift),
        )
        background_and_tip_group = DrawingGroup(background_and_tip)
        return RelativeDrawing(background_and_tip_group, relative.shift)

    @cached_property
    def _tip(self) -> Drawing | None:
        if not (tip := self.config.background.tip):
            return None

        if isinstance(tip, Drawing):
            tip_drawing = tip
        else:
            tip_drawing = tip.drawing
        return tip_drawing.flip(
            horizontal=not self._character_position.at_left,
            vertical=not self._character_position.at_top,
        )

    @cached_property
    @override
    def _background_top_left(self) -> Coordinate:
        if center := self.config.character_coordinate_override:
            return center.as_center_of(
                self._background_relative_to_text.drawing
            ).top_left

        shift_width, shift_height = (
            self.config.character_position_to_add_on_edge_center
        )
        character_left, character_top = self._character_position.coordinate
        background_width = self._background_relative_to_text.drawing.width.value
        left = (
            character_left
            + self._width_sign * shift_width
            - background_width / 2
        )

        # Clamp within screen width.
        pad_width = self.config.padding.width.value
        if left < pad_width:
            left = pad_width
        elif left + background_width > gui_width() - pad_width:
            left = gui_width().value - background_width - pad_width

        top = character_top + self._height_sign * shift_height
        if self._character_position.at_top:
            top += self._tip.height.value
        else:
            top -= self._background_relative_to_text.drawing.height.value
        return Coordinate(left, top)

    @property
    def _width_sign(self) -> Literal[-1, 1]:
        if self._character_position.at_left:
            return 1
        return -1

    @property
    def _height_sign(self) -> Literal[-1, 1]:
        if self._character_position.at_top:
            return 1
        return -1

    @cached_property
    @override
    def _avatar(self) -> Drawing | DrawingGroup | None:
        if self.config.avatar:
            return self.config.avatar
        return self.character.spec.avatar

    @cached_property
    @override
    def _name(self) -> str:
        if self.config.name_override:
            return self.config.name_override
        return self.character.display_name

    @cached_property
    def _character_position(self) -> _CharacterPosition:
        at_left = self._character_rectangle_on_screen.center in left_screen()
        if at_top := self._character_rectangle_on_screen.center in top_screen():
            coordinate = self._character_rectangle_on_screen.bottom_center
        else:
            coordinate = self._character_rectangle_on_screen.top_center

        return _CharacterPosition(
            coordinate=coordinate, at_top=at_top, at_left=at_left
        )

    @cached_property
    def _character_rectangle_on_screen(self) -> RectangleAreaOnScreen:
        rect = self.character.drawing_on_screen.visible_rectangle_area_on_screen
        if self.scene.drawing_on_screen_shift:
            return rect + self.scene.drawing_on_screen_shift
        return rect


@dataclass(frozen=True, kw_only=True)
class _CharacterPosition:
    coordinate: Coordinate
    at_top: bool
    at_left: bool
