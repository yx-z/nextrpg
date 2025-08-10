from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass
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
from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.draw.draw import RectangleOnScreen
from nextrpg.event.event_transformer import transform

type NpcEventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, "EventfulScene"]

type NpcEvent = Callable[[*NpcEventSpecParams], "EventGenerator | None"]


class NpcEventStartMode(Enum):
    CONFIRM = auto()
    COLLIDE = auto()


@dataclass_with_init(frozen=True)
class NpcEventSpec:
    event: NpcEvent
    start_mode: NpcEventStartMode = NpcEventStartMode.CONFIRM
    _: KW_ONLY = not_constructor_below()
    generator: "EventGenerator" = default(lambda self: transform(self.event))


@dataclass_with_init(frozen=True, kw_only=True)
class NpcSpec(_BaseCharacterSpec):
    character: CharacterDraw | Color | None = None
    event: NpcEventSpec | NpcEvent | None = None
    cyclic_walk: bool = True
    obstruct_others: bool = default(
        lambda self: isinstance(self.character, CharacterDraw)
    )

    @property
    def _event_spec(self) -> NpcEventSpec | None:
        if not self.event:
            return None
        if isinstance(self.event, NpcEventSpec):
            return self.event
        return NpcEventSpec(self.event)


@dataclass(frozen=True, kw_only=True)
class StrictNpcSpec(NpcSpec, CharacterSpec):
    event: NpcEventSpec | None


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
        event=spec._event_spec,
        config=spec.config,
        cyclic_walk=spec.cyclic_walk,
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
