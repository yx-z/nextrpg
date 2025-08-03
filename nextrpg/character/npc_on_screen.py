from collections.abc import Callable, Generator
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    CharacterSpec,
)
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.event.event_transformer import transform_and_compile
from nextrpg.global_config.character_config import CharacterConfig
from nextrpg.global_config.global_config import config

type NpcEventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, "EventfulScene"]
type NpcEventSpec = Callable[[*NpcEventSpecParams], None | NpcEventGenerator]

type NpcEventCallable = Callable[
    [NpcEventGenerator, "EventfulScene"], "RpgEventScene"
]
type NpcEventGenerator = Generator[NpcEventCallable, Any, None]


@dataclass(frozen=True)
class NpcSpec(CharacterSpec):
    event: NpcEventSpec | None = None
    config: CharacterConfig = field(default_factory=lambda: config().character)
    cyclic_walk: bool = True

    @cached_property
    def generator(self) -> Callable[[*NpcEventSpecParams], NpcEventGenerator]:
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
