from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg import RectangleAreaOnScreen
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config.say_event_config import (
    SayEventConfig,
    SayEventNineSliceBackgroundConfig,
)
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.rectangle_drawing import RectangleDrawing
from nextrpg.draw.relative_drawing import Anchor, RelativeDrawing
from nextrpg.draw.text import Text
from nextrpg.draw.text_group import TextGroup
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.geometry.coordinate import ORIGIN, Coordinate
from nextrpg.geometry.dimension import Width, WidthAndHeightScaling
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
            self._add_on_top_left
        )
        return tuple(
            drawing_on_screen
            for drawing_on_screen in drawing_on_screens
            if drawing_on_screen.drawing not in self._text.drawings
        )

    @cached_property
    def text_on_screen(self) -> TextOnScreen:
        coordinate = (
            self._add_on_top_left - self._background_relative_to_text.shift
        )
        return TextOnScreen(coordinate, self._text)

    @cached_property
    def _add_on_top_left(self) -> Coordinate:
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
        shift = self._text.bottom_left - self.config.padding.width
        return RelativeDrawing(self._avatar, shift.size, Anchor.BOTTOM_RIGHT)

    @cached_property
    def _name_relative_to_text(self) -> RelativeDrawing | None:
        if not self._name:
            return None
        text = Text(self._name, self.config.name_text_config)
        shift = Width(0) * -self.config.padding.height
        return RelativeDrawing(text.drawing_group, shift, Anchor.BOTTOM_LEFT)

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
        background_drawing = super()._background_relative_to_text.drawing
        if self._character_position.at_left:
            tip_left = (
                background_drawing.width / 2
                + self.config.background_edge_center_to_tip
            )
        else:
            tip_left = (
                background_drawing.width / 2
                - self.config.background_edge_center_to_tip
                - self._tip.width
            )

        if self._character_position.at_top:
            tip_top = -self._tip.height
        else:
            tip_top = background_drawing.height
        if isinstance(
            self.config.background, SayEventNineSliceBackgroundConfig
        ):
            if self._character_position.at_top:
                tip_top += self.config.background.nine_slice.top
            else:
                tip_top -= self.config.background.nine_slice.bottom
        tip_shift = tip_left * tip_top

        if isinstance(
            self.config.background, SayEventNineSliceBackgroundConfig
        ):
            if self._character_position.at_top:
                crop_size = (
                    self._tip.width * self.config.background.nine_slice.top
                )
            else:
                crop_size = (
                    self._tip.width * self.config.background.nine_slice.bottom
                )
            background_crop = RectangleAreaOnScreen(
                tip_shift.coordinate, crop_size
            )
            background_drawing = background_drawing.cut(background_crop)

        background_and_tip = (
            RelativeDrawing(background_drawing, ORIGIN),
            RelativeDrawing(self._tip, tip_shift),
        )
        background_and_tip_group = DrawingGroup(background_and_tip)

        shift = super()._background_relative_to_text.shift
        return RelativeDrawing(background_and_tip_group, shift)

    @cached_property
    def _tip(self) -> Drawing:
        if self._character_position.at_top:
            tip = self.config.background.tip_at_top
        else:
            tip = self.config.background.tip_at_bottom
        return tip.flip(horizontal=not self._character_position.at_left)

    @cached_property
    @override
    def _add_on_top_left(self) -> Coordinate:
        if center := self.config.character_coordinate_override:
            return center.as_center_of(
                self._background_relative_to_text.drawing
            ).top_left

        background_width = self._background_relative_to_text.drawing.width
        if self._character_position.at_left:
            left = (
                self._character_position.coordinate.left
                + self.config.character_position_to_add_on_edge_center.width
                - background_width / 2
            )
        else:
            left = (
                self._character_position.coordinate.left
                - self.config.character_position_to_add_on_edge_center.width
                - background_width / 2
            )
        # Clamp within screen width.
        pad_width = self.config.padding.width
        if left < pad_width:
            left = pad_width
        elif left + background_width > gui_width() - pad_width:
            left = gui_width() - background_width - pad_width

        if self._character_position.at_top:
            top = (
                self._character_position.coordinate.top
                + self.config.character_position_to_add_on_edge_center.height
            )
        else:
            top = (
                self._character_position.coordinate.top
                - self.config.character_position_to_add_on_edge_center.height
                - self._background_relative_to_text.drawing.height
            )
        return (left * top).coordinate

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
        rect = self.character.drawing_on_screen.visible_rectangle_area_on_screen
        if self.scene.drawing_on_screen_shift:
            rect += self.scene.drawing_on_screen_shift

        at_left = rect.center in left_screen()
        if at_top := rect.center in top_screen():
            coordinate = rect.bottom_center
        else:
            coordinate = rect.top_center

        return _CharacterPosition(
            coordinate=coordinate, at_top=at_top, at_left=at_left
        )


@dataclass(frozen=True, kw_only=True)
class _CharacterPosition:
    coordinate: Coordinate
    at_top: bool
    at_left: bool
