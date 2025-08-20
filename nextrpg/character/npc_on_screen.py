from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from enum import Enum, auto
from typing import Any, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
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
from nextrpg.draw.drawing import TransparentDrawing
from nextrpg.event.event_transformer import transform

type EventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, "EventfulScene"]

type RpgEvent = Callable[[*EventSpecParams], "EventGenerator | bool | None"]


class NpcEventStartMode(Enum):
    CONFIRM = auto()
    COLLIDE = auto()


@dataclass_with_init(frozen=True)
class EventSpec:
    event: RpgEvent
    start_mode: NpcEventStartMode = NpcEventStartMode.CONFIRM
    _: KW_ONLY = not_constructor_below()
    generator: "EventGenerator" = default(lambda self: transform(self.event))


@dataclass_with_init(frozen=True, kw_only=True)
class NpcSpec(_BaseCharacterSpec):
    character: CharacterDrawing | Color | None = None
    event: EventSpec | RpgEvent | None = None
    cyclic_walk: bool = True
    collide_with_others: bool = default(
        lambda self: isinstance(self.character, CharacterDrawing)
        and (
            not isinstance(
                drawing := self.character.drawing, TransparentDrawing
            )
            or not drawing.fully_transparent
        )
    )

    @property
    def event_spec(self) -> EventSpec | None:
        if not self.event:
            return None
        if isinstance(self.event, EventSpec):
            return self.event
        return EventSpec(self.event)


@dataclass(frozen=True, kw_only=True)
class StrictNpcSpec(NpcSpec, CharacterSpec):
    event: EventSpec | None


def to_strict(
    spec: NpcSpec, character_draw: CharacterDrawing | None = None
) -> StrictNpcSpec:
    assert (
        character := character_draw or spec.character
    ), f"'{spec.unique_name}' is missing CharacterDraw."
    return StrictNpcSpec(
        unique_name=spec.unique_name,
        character=character,
        collide_with_others=spec.collide_with_others,
        avatar=spec.avatar,
        display_name=spec.display_name,
        event=spec.event_spec,
        config=spec.config,
        cyclic_walk=spec.cyclic_walk,
    )


@dataclass(frozen=True, kw_only=True)
class NpcOnScreen(CharacterOnScreen):
    spec: StrictNpcSpec
    restart_event: bool = True

    @override
    @property
    def save_data(self) -> dict[str, Any]:
        return super().save_data | {"restart_event": self.restart_event}

    @override
    def update(self, save: dict[str, Any]) -> Self:
        character = super().update(save)
        restart_event = save["restart_event"]
        return replace(character, restart_event=restart_event)
