from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from functools import cached_property
from typing import override

from nextrpg.character.character_draw import CharacterDraw
from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    CharacterSpec,
    _BaseCharacterSpec,
)
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.color import Color
from nextrpg.draw.draw import RectangleOnScreen

type NpcEventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, "EventfulScene"]

type NpcEvent = Callable[[*NpcEventSpecParams], "EventGenerator | None"]


class NpcEventStartMode(Enum):
    CONFIRM = auto()
    COLLIDE = auto()


@dataclass(frozen=True)
class NpcEventSpec:
    function: NpcEvent
    start_mode: NpcEventStartMode = NpcEventStartMode.CONFIRM


@dataclass(frozen=True, kw_only=True)
class NpcSpec(_BaseCharacterSpec):
    # This field is not conformant with CharacterSpec
    character: CharacterDraw | Color | None = None
    event: NpcEventSpec | NpcEvent | None = None
    cyclic_walk: bool = True

    @property
    def init_generator(
        self,
    ) -> Callable[[*NpcEventSpecParams], "EventGenerator"] | None:
        if not self.event:
            return None
        if isinstance(self.event, NpcEventSpec):
            return self.event.function
        return self.event


@dataclass(frozen=True, kw_only=True)
class StrictNpcSpec(NpcSpec, CharacterSpec):
    generator: Callable[[*NpcEventSpecParams], "EventGenerator"] | None


def to_strict(
    spec: NpcSpec, character_draw: CharacterDraw | None = None
) -> StrictNpcSpec:
    assert (
        character_draw or spec.character
    ), f"'{spec.object_name}' is missing CharacterDraw."
    return StrictNpcSpec(
        object_name=spec.object_name,
        character=character_draw or spec.character,
        obstruct_others=spec.obstruct_others,
        collide_with_others=spec.collide_with_others,
        avatar=spec.avatar,
        display_name=spec.display_name,
        event=spec.event,
        config=spec.config,
        cyclic_walk=spec.cyclic_walk,
        generator=spec.init_generator,
    )


@dataclass(frozen=True, kw_only=True)
class NpcOnScreen(CharacterOnScreen):
    spec: StrictNpcSpec

    @override
    @cached_property
    def start_event_rectangle(self) -> RectangleOnScreen | None:
        if self.spec.event:
            return super().start_event_rectangle
        return None
