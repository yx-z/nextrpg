from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    CharacterSpec,
)
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.dimension import PixelPerMillisecond
from nextrpg.core.time import Millisecond
from nextrpg.event.event_transformer import transform_and_compile
from nextrpg.global_config.global_config import config

type RpgEventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, "EventfulScene"]

type RpgEventSpec = Callable[[*RpgEventSpecParams], None | RpgEventGenerator]

type RpgEventGenerator = Generator[RpgEventCallable, Any, None]

type RpgEventCallable = Callable[
    [RpgEventGenerator, "EventfulScene"], "RpgEventScene"
]


@dataclass(frozen=True, kw_only=True)
class NpcSpec(CharacterSpec):
    event: RpgEventSpec
    move_speed: PixelPerMillisecond = field(
        default_factory=lambda: config().character.move_speed
    )
    idle_duration: Millisecond = field(
        default_factory=lambda: config().character.idle_duration
    )
    move_duration: Millisecond = field(
        default_factory=lambda: config().character.move_duration
    )
    cyclic_walk: bool = True

    @cached_property
    def generator(self) -> Callable[[*RpgEventSpecParams], RpgEventGenerator]:
        fun = self.event
        ctx = fun.__globals__ | {
            v: c.cell_contents
            for v, c in zip(fun.__code__.co_freevars, fun.__closure__ or ())
        }
        exec(transform_and_compile(fun), ctx)
        return ctx[fun.__name__]


@dataclass(frozen=True, kw_only=True)
class NpcOnScreen(CharacterOnScreen):
    spec: NpcSpec
