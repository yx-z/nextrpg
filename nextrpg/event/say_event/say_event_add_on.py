from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg.animation.animation_on_screen import AnimationOnScreen
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config.event.say_event_config import (
    AvatarPosition,
    SayEventConfig,
    SayEventNineSliceBackgroundConfig,
)
from nextrpg.drawing.drawing_group import DrawingGroup
from nextrpg.drawing.drawing_on_screens import (
    DrawingOnScreens,
    drawing_on_screens,
)
from nextrpg.drawing.rectangle_drawing import RectangleDrawing
from nextrpg.drawing.shifted_sprite import ShiftedSprite
from nextrpg.drawing.sprite import Sprite
from nextrpg.drawing.sprite_on_screen import SpriteOnScreen
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.drawing.text_on_screen import TextOnScreen
from nextrpg.event.eventful_scene import EventfulScene
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.scaling import WidthAndHeightScaling
from nextrpg.gui.screen_area import (
    left_screen_area,
    screen_area,
    top_screen_area,
)


@dataclass(frozen=True)
class SayEventAddOn:
    config: SayEventConfig
    message: str | Text | Sprite | TextGroup

    @cached_property
    def background(self) -> SpriteOnScreen:
        contents = [
            drawing
            for drawing in [
                self._text.drawing,
                self._name_relative_to_text,
                self._avatar_relative_to_text,
            ]
            if drawing
        ]
        content = DrawingGroup(tuple(contents))

        background = self._background_relative_to_text.resource
        shift = self._background_relative_to_text.offset_size
        add_on_group = DrawingGroup((background, content - shift))
        return _Background(
            coordinate=self._add_on_top_left,
            resource=add_on_group,
            text=self._text,
        )

    @cached_property
    def text_on_screen(self) -> TextOnScreen:
        top_left = (
            self._add_on_top_left
            - self._background_relative_to_text.offset_size
        )
        if isinstance(self._text, Text | TextGroup):
            text = self._text
        else:
            text = TextGroup(self._text)
        return text.text_on_screen(top_left)

    @cached_property
    def _add_on_top_left(self) -> Coordinate:
        return self.config.scene_coordinate.as_center_of(
            self._background_relative_to_text.resource
        ).top_left

    @cached_property
    def _avatar(self) -> Sprite | None:
        return self.config.avatar

    @cached_property
    def _name(self) -> str | None:
        return self.config.name_override

    @cached_property
    def _background_relative_to_text(self) -> ShiftedSprite:
        shift = -self.config.padding
        size = self._text.size + self.config.padding * WidthAndHeightScaling(2)
        if self._name_relative_to_text:
            extra_height = (
                self._name_relative_to_text.resource.height
                + self.config.padding.height
            )
            shift -= extra_height
            size += extra_height
        if self._avatar_relative_to_text:
            extra_width = (
                self._avatar_relative_to_text.resource.size.width
                + self.config.padding.width
            )
            if self.config.avatar_position is AvatarPosition.LEFT:
                shift -= extra_width
            size += extra_width

        if isinstance(
            self.config.background, SayEventNineSliceBackgroundConfig
        ):
            rect = self.config.background.nine_slice.stretch(size)
        else:
            rect = RectangleDrawing(
                size,
                self.config.background.color,
                border_radius=self.config.background.border_radius,
            ).drawing
        return rect + shift

    @cached_property
    def _avatar_relative_to_text(self) -> ShiftedSprite | None:
        if not self._avatar:
            return None
        match self.config.avatar_position:
            case AvatarPosition.LEFT:
                shift = self._text.bottom_left - self.config.padding.width
                return self._avatar.shift(shift, Anchor.BOTTOM_RIGHT)
            case AvatarPosition.RIGHT:
                shift = self._text.bottom_right + self.config.padding.width
                return self._avatar.shift(shift, Anchor.BOTTOM_LEFT)

    @cached_property
    def _name_relative_to_text(self) -> ShiftedSprite | None:
        if not self._name:
            return None
        text = Text(self._name, self.config.name_text_config)
        return text.drawing.shift(
            -self.config.padding.height, Anchor.BOTTOM_LEFT
        )

    @cached_property
    def _text(self) -> Text | Sprite | TextGroup:
        if isinstance(self.message, str):
            return Text(self.message, self.config.text_config)
        return self.message


@dataclass(frozen=True)
class SayEventCharacterAddOn(SayEventAddOn):
    scene: EventfulScene
    character: CharacterOnScreen

    @override
    @cached_property
    def _background_relative_to_text(self) -> ShiftedSprite:
        background_drawing = super()._background_relative_to_text.resource
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
            background_crop = tip_shift.coordinate.as_top_left_of(
                crop_size
            ).rectangle_area_on_screen
            background_drawing = background_drawing.cut(background_crop)

        background_and_tip_group = DrawingGroup(
            (background_drawing, self._tip + tip_shift)
        )

        background_shift = super()._background_relative_to_text.offset_size
        return background_and_tip_group + background_shift

    @cached_property
    def _tip(self) -> Sprite:
        if self._character_position.at_top:
            tip = self.config.background.tip_at_top
        else:
            tip = self.config.background.tip_at_bottom
        return tip.flip(horizontal=not self._character_position.at_left)

    @override
    @cached_property
    def _add_on_top_left(self) -> Coordinate:
        if center := self.config.character_coordinate_input:
            return center.as_center_of(
                self._background_relative_to_text.resource
            ).top_left

        background_width = self._background_relative_to_text.resource.width
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
        if left.width < pad_width:
            left = pad_width.x_axis
        elif left + background_width > screen_area().right - pad_width:
            left = screen_area().right - background_width - pad_width

        if self._character_position.at_top:
            top = (
                self._character_position.coordinate.top
                + self.config.character_position_to_add_on_edge_center.height
            )
        else:
            top = (
                self._character_position.coordinate.top
                - self.config.character_position_to_add_on_edge_center.height
                - self._background_relative_to_text.resource.height
            )
        return left @ top

    @cached_property
    @override
    def _avatar(self) -> Sprite | None:
        if self.config.avatar:
            return self.config.avatar
        return self.character.spec.avatar

    @cached_property
    @override
    def _name(self) -> str:
        if self.config.name_override:
            return self.config.name_override
        return self.character.name

    @cached_property
    def _character_position(self) -> _CharacterPosition:
        if self.scene.drawing_on_screens_shift:
            rect = (
                self.character.drawing_on_screen.rectangle_area_on_screen
            ) + self.scene.drawing_on_screens_shift
        else:
            rect = self.character.drawing_on_screen.rectangle_area_on_screen

        at_left = rect.center in left_screen_area()
        if at_top := rect.center in top_screen_area():
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


@dataclass(frozen=True, kw_only=True)
class _Background(AnimationOnScreen):
    text: Sprite

    @override
    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        return drawing_on_screens(
            drawing_on_screen
            for drawing_on_screen in super().drawing_on_screens
            if drawing_on_screen.drawing not in self.text.drawings
        )
