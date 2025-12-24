from dataclasses import dataclass, replace
from functools import cached_property
from typing import override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.config.config import config
from nextrpg.config.event.say_event_config import (
    AvatarPosition,
    SayEventConfig,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.sprite import Sprite
from nextrpg.drawing.text import Text
from nextrpg.drawing.text_group import TextGroup
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.event_scene import (
    EventScene,
    register_rpg_event_scene,
)
from nextrpg.event.say_event.say_event_add_on import (
    SayEventAddOn,
    SayEventCharacterAddOn,
)
from nextrpg.event.say_event.say_event_state import (
    SayEventFadeInState,
)
from nextrpg.game.game_state import GameState
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.size import Size
from nextrpg.scene.scene import Scene

type SayEventArg = str | Coordinate | Millisecond | Size | Sprite | AvatarPosition | SayEventConfig


@dataclass(frozen=True)
class SayEventScene(EventScene):
    character_or_scene: CharacterOnScreen | Scene
    message: str | Text | Sprite | TextGroup
    args: tuple[SayEventArg, ...] = ()

    @override
    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        return self._state.drawing_on_screens

    @override
    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState]:
        return self._state.tick(time_delta, state)

    @override
    def event(
        self, event: BaseEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        return self._state.event(event, state)

    @cached_property
    def config(self) -> SayEventConfig:
        cfg = config().event.say_event
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
) -> None: ...


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
        case Sprite():
            return replace(cfg, avatar_input=arg)
        case str():
            return replace(cfg, name_override=arg)
    raise ValueError(
        f"Expect str | Coordinate | Millisecond | AnimationLike | AvatarPosition | SayEventConfig. Got {arg}"
    )
