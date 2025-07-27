from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import override

from nextrpg.core.coordinate import Coordinate
from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.draw.draw import DrawOnScreen
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

    @abstractmethod
    def background(self) -> tuple[DrawOnScreen, ...]:
        """"""

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


class SceneAddOn(AddOn):

    @cached_property
    @override
    def background(self) -> tuple[DrawOnScreen, ...]:
        add_on_on_screen = GroupOnScreen(self.background_top_left, self.add_on)
        text_add_on = add_on_on_screen.group_draw_on_screens(self.text.group)
        res = tuple(
            d for d in add_on_on_screen.draw_on_screens if d not in text_add_on
        )
        return res

    @cached_property
    @override
    def background_top_left(self) -> Coordinate:
        center = self.config.coordinate or self.config.default_scene_coordinate
        return (
            center
            - self.background_relative_to.draw.size.all_dimension_scale(0.5)
        )


@dataclass(frozen=True)
class CharacterAddOn(SceneAddOn):
    scene: Scene
    character: CharacterOnScreen

    @cached_property
    @override
    def background(self) -> tuple[DrawOnScreen, ...]: ...

    @cached_property
    @override
    def background_top_left(self) -> Coordinate: ...
