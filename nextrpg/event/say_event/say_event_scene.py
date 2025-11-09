from dataclasses import dataclass, replace
from functools import cached_property
from typing import override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config.config import config
from nextrpg.config.rpg_event.say_event_config import (
    AvatarPosition,
    SayEventConfig,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_like import AnimationLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.event.io_event import IoEvent
from nextrpg.event.rpg_event_scene import (
    RpgEventScene,
    register_rpg_event_scene,
)
from nextrpg.event.say_event.say_event_add_on import (
    SayEventAddOn,
    SayEventCharacterAddOn,
)
from nextrpg.event.say_event.say_event_state import (
    SayEventFadeInState,
)
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.dimension import Size
from nextrpg.scene.scene import Scene

type SayEventArg = str | Coordinate | Millisecond | Size | AnimationLike | AvatarPosition | SayEventConfig


@dataclass(frozen=True)
class SayEventScene(RpgEventScene):
    character_or_scene: CharacterOnScreen | Scene
    message: str | Text | TextGroup
    args: tuple[SayEventArg, ...] = ()

    @override
    @cached_property
    def drawing_on_screens(self) -> list[DrawingOnScreen]:
        return self._state.drawing_on_screens

    @override
    def tick(self, time_delta: Millisecond) -> Scene:
        return self._state.tick(time_delta)

    @override
    def event(self, event: IoEvent) -> Scene:
        return self._state.event(event)

    @cached_property
    def config(self) -> SayEventConfig:
        cfg = config().say_event
        for arg in self.args:
            cfg = _update_config(cfg, arg)
        return cfg

    @cached_property
    def _add_on(self) -> SayEventAddOn:
        if isinstance(self.character_or_scene, CharacterOnScreen):
            name = self.character_or_scene.spec.unique_name
            ticked_character = self.parent.get_character(name)
            return SayEventCharacterAddOn(
                self.config, self.message, self.parent, ticked_character
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
            parent=self.parent,
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
        case AvatarPosition():
            return replace(cfg, avatar_position=arg)
        case int():
            return replace(cfg, text_delay=arg)
        case Coordinate():
            return replace(
                cfg,
                scene_coordinate_override=arg,
                character_coordinate_override=arg,
            )
        case AnimationLike():
            return replace(cfg, avatar_input=arg)
        case str():
            return replace(cfg, name_override=arg)
    raise ValueError(
        f"Expect str | Coordinate | Millisecond | AnimationLike | AvatarPosition | SayEventConfig. Got {arg}"
    )
