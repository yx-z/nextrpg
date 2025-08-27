from dataclasses import dataclass, replace
from functools import cached_property
from typing import override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config.config import config
from nextrpg.config.say_event_config import SayEventConfig
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.draw.text import Text
from nextrpg.draw.text_group import TextGroup
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.scene.rpg_event.rpg_event_scene import (
    RpgEventScene,
    register_rpg_event_scene,
)
from nextrpg.scene.rpg_event.say_event.say_event_add_on import (
    SayEventAddOn,
    SayEventCharacterAddOn,
)
from nextrpg.scene.rpg_event.say_event.say_event_state import (
    SayEventFadeInState,
)
from nextrpg.scene.scene import Scene

type SayEventArg = str | Coordinate | Size | Drawing | SayEventConfig


@dataclass(frozen=True)
class SayEventScene(RpgEventScene):
    character_or_scene: CharacterOnScreen | Scene
    message: str | Text | TextGroup
    args: tuple[SayEventArg, ...] = ()

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return self._state.drawing_on_screens

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
    def _add_on(self) -> SayEventAddOn:
        if isinstance(self.character_or_scene, CharacterOnScreen):
            name = self.character_or_scene.spec.unique_name
            ticked_character = self.scene.get_character(name)
            return SayEventCharacterAddOn(
                self.config, self.message, self.scene, ticked_character
            )
        return SayEventAddOn(self.config, self.message)

    @cached_property
    def _state(self) -> SayEventFadeInState:
        if isinstance(self.character_or_scene, CharacterOnScreen):
            unique_name = self.character_or_scene.spec.unique_name
        else:
            unique_name = None

        return SayEventFadeInState(
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
        case int():
            return replace(cfg, text_delay=arg)
        case Coordinate():
            return replace(
                cfg,
                scene_coordinate_override=arg,
                character_coordinate_override=arg,
            )
        case Drawing():
            return replace(cfg, avatar=arg)
        case str():
            return replace(cfg, name_override=arg)
    raise ValueError(
        f"Expect str | Coordinate | Draw | SayEventConfig. Got {arg}"
    )
