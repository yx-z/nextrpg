from dataclasses import dataclass, replace
from functools import cached_property
from typing import override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.core.dimension import Size
from nextrpg.core.time import Millisecond
from nextrpg.draw.draw import Draw, DrawOnScreen
from nextrpg.draw.text import Text, TextGroup
from nextrpg.global_config.global_config import config
from nextrpg.global_config.say_event_config import SayEventConfig
from nextrpg.scene.rpg_event.eventful_scene import (
    RpgEventScene,
    register_rpg_event_scene,
)
from nextrpg.scene.rpg_event.say_event.say_event_add_on import (
    AddOn,
    CharacterAddOn,
)
from nextrpg.scene.rpg_event.say_event.say_event_state import FadeInState
from nextrpg.scene.scene import Scene

type SayEventArg = str | Coordinate | Size | Draw | SayEventConfig


@dataclass(frozen=True)
class SayEventScene(RpgEventScene):
    character_or_scene: CharacterOnScreen | Scene
    message: str | Text | TextGroup
    args: tuple[SayEventArg, ...] = ()

    @override
    @cached_property
    def draw_on_screens(self) -> tuple[DrawOnScreen, ...]:
        return self._state.draw_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        return self._state.tick(time_delta)

    @cached_property
    def config(self) -> SayEventConfig:
        cfg = config().say_event
        if isinstance(self.args, str):
            cfg = _update_config(cfg, self.args)
        else:
            for arg in self.args:
                cfg = _update_config(cfg, arg)
        return cfg

    @cached_property
    def _add_on(self) -> AddOn:
        if isinstance(self.character_or_scene, CharacterOnScreen):
            name = self.character_or_scene.spec.unique_name
            ticked_character = self.scene.get_character(name)
            return CharacterAddOn(
                self.config, self.message, self.scene, ticked_character
            )
        return AddOn(self.config, self.message)

    @cached_property
    def _state(self) -> FadeInState:
        if isinstance(self.character_or_scene, CharacterOnScreen):
            unique_name = self.character_or_scene.spec.unique_name
        else:
            unique_name = None

        return FadeInState(
            generator=self.generator,
            scene=self.scene,
            unique_name=unique_name,
            background=self._add_on.background,
            text_on_screen=self._add_on.text_on_screen,
            config=self.config,
        )


@register_rpg_event_scene(SayEventScene)
def say(
    character_or_scene: CharacterOnScreen | Scene,
    message: str | Text | TextGroup,
    args: tuple[SayEventArg, ...],
) -> Scene: ...


def _update_config(cfg: SayEventConfig, arg: SayEventArg) -> SayEventConfig:
    match arg:
        case SayEventConfig():
            return arg
        case Coordinate():
            return replace(cfg, coordinate_override=arg)
        case Draw():
            return replace(cfg, avatar=arg)
        case str():
            return replace(cfg, name_override=arg)
    raise ValueError(
        f"Expect str | Coordinate | Draw | SayEventConfig. Got {arg}"
    )
