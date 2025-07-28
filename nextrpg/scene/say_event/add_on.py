from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Literal, override

from nextrpg import PolygonOnScreen, left_screen
from nextrpg.gui.area import gui_width, top_screen
from nextrpg.core.coordinate import Coordinate
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.draw.draw import DrawOnScreen, RectangleOnScreen
from nextrpg.draw.group import Group, GroupOnScreen, DrawRelativeTo
from nextrpg.draw.text import Text
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class AddOn(ABC):
    text: Text
    add_on: Group
    background_relative_to: DrawRelativeTo
    config: SayEventConfig

    @cached_property
    def background(self) -> tuple[DrawOnScreen, ...]:
        add_on_on_screen = GroupOnScreen(self.background_top_left, self.add_on)
        text_add_on = add_on_on_screen.group_draw_on_screens(self.text.group)
        res = tuple(
            d for d in add_on_on_screen.draw_on_screens if d not in text_add_on
        )
        return res

    @property
    @abstractmethod
    def background_top_left(self) -> Coordinate:
        """"""

    @cached_property
    def text_on_screen(self) -> TextOnScreen:
        coord = (
            self.background_top_left + self.background_relative_to.relative_to
        )
        return TextOnScreen(coord, self.text)

    def _center_to_top_left(self, center: Coordinate) -> Coordinate:
        size = self.background_relative_to.draw.size.all_dimension_scale(0.5)
        return center - size


class SceneAddOn(AddOn):
    @cached_property
    @override
    def background_top_left(self) -> Coordinate:
        center = self.config.coordinate or self.config.default_scene_coordinate
        return self._center_to_top_left(center)


@dataclass(frozen=True)
class CharacterAddOn(SceneAddOn):
    scene: Scene
    character: CharacterOnScreen

    @cached_property
    @override
    def background(self) -> tuple[DrawOnScreen, ...]:
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
                self.background_top_left.top
                + self.background_relative_to.draw.height
            )

        tip_coord = Coordinate(tip_left, tip_top)
        base_coord1 = Coordinate(base_coord1_left, base_coord_top)
        base_coord2 = Coordinate(base_coord2_left, base_coord_top)
        tip = PolygonOnScreen((tip_coord, base_coord1, base_coord2))
        tip_draw = tip.fill(self.config.background)

        return (tip_draw,) + super().background

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
        background_width, background_height = (
            self.background_relative_to.draw.size
        )
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
        if s := self.scene.draw_on_screen_shift:
            return rect + s
        return rect


@dataclass(frozen=True)
class _CharacterPosition:
    coordinate: Coordinate
    is_top: bool
    height_sign: Literal[1, -1]
