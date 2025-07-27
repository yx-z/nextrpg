from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from nextrpg import Coordinate, Polygon, left_screen, top_screen
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.draw.draw_on_screen import DrawOnScreen, Rectangle
from nextrpg.scene.scene import Scene
from nextrpg.core.dimension import Size
from nextrpg.draw.text_on_screen import TextOnScreen
from nextrpg.draw.drawing_group import DrawingGroup, DrawingGroupOnScreen
from nextrpg.draw.text import Text
from nextrpg.global_config.say_event_config import SayEventConfig


@dataclass(frozen=True)
class SceneSay:
    text: Text
    add_on: DrawingGroup
    config: SayEventConfig

    @cached_property
    def background(self) -> tuple[DrawOnScreen, ...]:
        padding_size = Size(self.config.padding, self.config.padding)
        top_left = self.text_on_screen.top_left - padding_size
        size = self.add_on.size + padding_size.all_dimension_scale(2)
        rect = Rectangle(top_left, size).fill(
            self.config.background, self.config.border_radius
        )

        add_on_on_screen = DrawingGroupOnScreen(top_left, self.add_on)
        text_add_on = add_on_on_screen.draw_on_screen_group(
            self.text.drawing_group
        )
        add_on_without_text = tuple(
            d for d in add_on_on_screen.draw_on_screens if d not in text_add_on
        )
        return (rect,) + add_on_without_text

    @cached_property
    def text_on_screen(self) -> TextOnScreen:
        center = self.config.coordinate or self.config.default_scene_coordinate
        top_left = center - self.text.size.all_dimension_scale(0.5)
        return TextOnScreen(top_left, self.text)


@dataclass(frozen=True)
class CharacterSay:
    text: Text
    add_on: DrawingGroup
    scene: Scene
    character: CharacterOnScreen
    config: SayEventConfig

    @cached_property
    def background(self) -> tuple[DrawOnScreen, ...]:
        rect = self._tail_and_rectangle.rectangle
        padding_size = Size(self.config.padding, self.config.padding)
        top_left = rect.top_left + padding_size
        add_on_on_screen = DrawingGroupOnScreen(top_left, self.add_on)
        text_add_on = add_on_on_screen.draw_on_screen_group(
            self.text.drawing_group
        )
        add_on_without_text = tuple(
            d for d in add_on_on_screen.draw_on_screens if d not in text_add_on
        )

        background = self.config.background
        tail = self._tail_and_rectangle.tail.fill(background)
        rect_draw = rect.fill(background, self.config.border_radius)
        return (tail, rect_draw) + add_on_without_text

    @cached_property
    def _tail_and_rectangle(self) -> _TailAndRectangle:
        if s := self.scene.draw_on_screen_shift:
            character_coord = self.character.coordinate - s
        else:
            character_coord = self.character.coordinate

        character_rect = self.character.draw_on_screen.visible_rectangle
        if character_coord in top_screen():
            base_coord = character_rect.bottom_center + self.config.shift
            height_sign = 1
        else:
            base_coord = character_rect.top_center - self.config.shift
            height_sign = -1

        if character_coord in left_screen():
            width_sign = -1
        else:
            width_sign = 1

        tail_width, tail_height = self.config.tail_size
        tail_coord1 = base_coord + Size(
            width_sign * tail_width, height_sign * tail_height
        )
        tail_coord2 = base_coord + Size(
            width_sign * self.config.tail_tip_shift, height_sign * tail_height
        )
        tail = Polygon((base_coord, tail_coord1, tail_coord2))

        padding = self.config.padding
        padding_size = Size(padding, padding)
        rect_left = max(padding, base_coord.left - self.add_on.size.width / 2)
        rect_top = base_coord.top + height_sign * self.add_on.size.height / 2
        rect_coord = Coordinate(rect_left, rect_top)
        rect_size = self.add_on.size + padding_size.all_dimension_scale(2)
        rect = Rectangle(rect_coord, rect_size)

        return _TailAndRectangle(tail, rect)

    @cached_property
    def text_on_screen(self) -> TextOnScreen:
        rect = self._tail_and_rectangle.rectangle
        padding_size = Size(self.config.padding, self.config.padding)
        top_left = rect.top_left + padding_size
        return TextOnScreen(top_left, self.text)


@dataclass(frozen=True)
class _TailAndRectangle:
    tail: Polygon
    rectangle: Rectangle
