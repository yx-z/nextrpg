from dataclasses import dataclass, replace
from functools import cached_property
from typing import Literal, override

from nextrpg.global_config.text_config import TextConfig
from nextrpg.draw.draw import Draw, PolygonOnScreen
from nextrpg.core.dimension import Size
from nextrpg.gui.area import gui_width, top_screen, left_screen
from nextrpg.core.coordinate import Coordinate
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.draw.draw import DrawOnScreen, RectangleDraw, RectangleOnScreen
from nextrpg.draw.group import Group, GroupOnScreen, DrawRelativeTo
from nextrpg.draw.text import Text
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class AddOn:
    config: SayEventConfig
    message: str

    @cached_property
    def background(self) -> tuple[DrawOnScreen, ...]:
        add_on_on_screen = GroupOnScreen(self.background_top_left, self._group)
        text_add_on = add_on_on_screen.group_draw_on_screens(self._text.group)
        return tuple(
            d for d in add_on_on_screen.draw_on_screens if d not in text_add_on
        )

    @cached_property
    def text_on_screen(self) -> TextOnScreen:
        coord = self.background_top_left + self._background.relative_to
        return TextOnScreen(coord, self._text)

    @cached_property
    def background_top_left(self) -> Coordinate:
        center = self.config.coordinate or self.config.default_scene_coordinate
        return self._center_to_top_left(center)

    def _center_to_top_left(self, center: Coordinate) -> Coordinate:
        size = self._background.draw.size.all_dimension_scale(0.5)
        return center - size

    @cached_property
    def _group(self) -> Group:
        leader = self._text.group
        followers = tuple(
            d for d in (self._avatar_relative, self._name_relative) if d
        )
        content = Group(leader, followers)
        background, shift = self._background
        return Group(background, DrawRelativeTo(content, shift))

    @cached_property
    def _background(self) -> DrawRelativeTo:
        padding = self.config.padding
        text_width, text_height = self._text.size
        relative_to_width = padding
        relative_to_height = padding

        rect_height = text_height + 2 * padding
        if self._name:
            extra_height = self._name_relative.draw.size.height + padding
            relative_to_height += extra_height
            rect_height += extra_height

        rect_width = text_width + 2 * padding
        if self._avatar:
            extra_width = self._avatar.size.width + padding
            relative_to_width += extra_width
            rect_width += extra_width

        size = Size(rect_width, rect_height)
        rect = RectangleDraw(
            size, self.config.background, self.config.border_radius
        )
        shift = Size(relative_to_width, relative_to_height)
        return DrawRelativeTo(rect, shift)

    @cached_property
    def _avatar(self) -> Draw | Group | None:
        return self.config.avatar

    @cached_property
    def _avatar_relative(self) -> DrawRelativeTo | None:
        if not self._avatar:
            return None
        width, height = self._avatar.size
        left_shift = -self.config.padding - width
        top_shift = self._text.size.height - height
        shift = Size(left_shift, top_shift)
        return DrawRelativeTo(self._avatar, shift)

    @cached_property
    def _name(self) -> str | None:
        return self.config.name_override

    @cached_property
    def _name_relative(self) -> DrawRelativeTo | None:
        if not self._name:
            return None

        text_config = replace(self._text_config, color=self.config.name_color)
        text = Text(self._name, text_config)
        name_height = text.size.height
        shift = Size(0, -name_height - self.config.padding)
        return DrawRelativeTo(text.group, shift)

    @cached_property
    def _text(self) -> Text:
        return Text(self.message, self._text_config)

    @cached_property
    def _text_config(self) -> TextConfig:
        return self.config.text or self.config.default_text_config


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
        if self._character_on_screen.center in left_screen():
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

        if self._character_edge.is_top:
            base_coord_top = self.background_top_left.top
        else:
            base_coord_top = (
                self.background_top_left.top + self._background.draw.height
            )

        tip_coord = Coordinate(tip_left, tip_top)
        base_coord1 = Coordinate(base_coord1_left, base_coord_top)
        base_coord2 = Coordinate(base_coord2_left, base_coord_top)
        tip = PolygonOnScreen((tip_coord, base_coord1, base_coord2))
        return tip.fill(self.config.background)

    @cached_property
    @override
    def background_top_left(self) -> Coordinate:
        if center := self.config.coordinate:
            return self._center_to_top_left(center)

        character_left, character_top = self._character_edge.coordinate
        background_shift_width, background_shift_height = (
            self.config.add_on.add_on_shift
        )
        edge = (
            character_top
            + self._character_edge.height_sign * background_shift_height
        )
        background_width, background_height = self._background.draw.size
        if self._character_edge.is_top:
            top = edge - background_height
        else:
            top = edge

        center = character_left - background_shift_width
        left = center - background_width / 2
        padding = self.config.padding
        if left < padding:
            left = padding
        elif center + background_width / 2 > gui_width() - padding:
            left = gui_width() - background_width - padding

        return Coordinate(left, top)

    @cached_property
    def _character_edge(self) -> _CharacterPosition:
        rect = self._character_on_screen
        if rect.center in top_screen():
            return _CharacterPosition(rect.bottom_center, True, 1)
        return _CharacterPosition(rect.top_center, False, -1)

    @cached_property
    def _character_on_screen(self) -> RectangleOnScreen:
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


@dataclass(frozen=True)
class _CharacterPosition:
    coordinate: Coordinate
    is_top: bool
    height_sign: Literal[1, -1]
