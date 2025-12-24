from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from enum import auto
from functools import cached_property
from typing import TYPE_CHECKING, Any, Generator, Literal, Self, override

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_spec import CharacterSpec, _BaseCharacterSpec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.polygon_character_drawing import PolygonCharacterDrawing
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.save import (
    HasSaveData,
    LoadFromSave,
    LoadFromSaveEnum,
    UpdateFromSave,
)
from nextrpg.drawing.color import Color
from nextrpg.event.event_transformer import transform_event

if TYPE_CHECKING:
    from nextrpg.character.npc_on_screen import NpcOnScreen
    from nextrpg.event.event_scene import (
        DISMISS_EVENT,
        EventGenerator,
        EventScene,
    )
    from nextrpg.event.eventful_scene import EventfulScene
    from nextrpg.game.game_state import GameState


type EventSpecParams = tuple[
    PlayerOnScreen, NpcOnScreen, EventfulScene, GameState
]
type RpgEvent = Callable[
    [*EventSpecParams], EventGenerator | Literal[DISMISS_EVENT] | None | Any
]


class NpcEventStartMode(LoadFromSaveEnum):
    CONFIRM = auto()
    COLLIDE = auto()


@dataclass_with_default(frozen=True)
class EventSpec(UpdateFromSave[dict[str, Any]]):
    event: RpgEvent
    start_mode: NpcEventStartMode = NpcEventStartMode.CONFIRM
    _: KW_ONLY = private_init_below()
    generator: Callable[
        [*EventSpecParams], Generator[EventScene, Any, None]
    ] = default(lambda self: transform_event(self.event))

    def with_event(self, event: RpgEvent) -> Self:
        generator = transform_event(event)
        return replace(self, event=event, generator=generator)

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return {
            "start_mode": self.start_mode.save_data,
            "event": (
                self.event.save_data
                if isinstance(self.event, HasSaveData)
                else None
            ),
        }

    @override
    def update_this_class_from_save(self, data: dict[str, Any]) -> Self:
        start_mode = NpcEventStartMode.load_from_save(data["start_mode"])
        event_data = data["event"]
        match self.event:
            case LoadFromSave():
                event = self.event.load_from_save(event_data)
            case UpdateFromSave():
                event = self.event.update_from_save(event_data)
            case _:
                event = self.event
        new_event = self.with_event(event)
        return replace(new_event, start_mode=start_mode)


@dataclass_with_default(frozen=True, kw_only=True)
class NpcSpec(_BaseCharacterSpec):
    character_drawing: CharacterDrawing | Color | None = None
    event: EventSpec | RpgEvent | None = None
    cyclic_walk: bool = True
    collide_with_others: bool = default(
        lambda self: isinstance(self.character_drawing, CharacterDrawing)
        and not isinstance(self.character_drawing, PolygonCharacterDrawing)
    )


@dataclass(frozen=True, kw_only=True)
class StrictNpcSpec(NpcSpec, CharacterSpec, UpdateFromSave[dict[str, Any]]):
    _: KW_ONLY = private_init_below()
    event_spec: EventSpec | None = default(lambda self: self._init_event_spec)

    def with_event_spec(self, event_spec: EventSpec | RpgEvent) -> Self:
        if not isinstance(event_spec, EventSpec):
            if self.event_spec:
                event_spec = self.event_spec.with_event(event_spec)
            else:
                event_spec = EventSpec(event_spec)
        return replace(self, event_spec=event_spec)

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return {
            "unique_name": self.unique_name,
            "event_spec": (
                self.event_spec.save_data if self.event_spec else None
            ),
        }

    @override
    def update_this_class_from_save(self, data: dict[str, Any]) -> Self:
        unique_name = data["unique_name"]
        if self.event_spec:
            event_spec = self.event_spec.update_from_save(data["event_spec"])
        else:
            event_spec = self.event_spec
        return replace(self, unique_name=unique_name, event_spec=event_spec)

    @property
    def _init_event_spec(self) -> EventSpec | None:
        if not self.event:
            return None
        if isinstance(self.event, EventSpec):
            return self.event
        return EventSpec(self.event)


def to_strict_npc_spec(
    spec: NpcSpec, character_drawing: CharacterDrawing | None = None
) -> StrictNpcSpec:
    character_drawing = character_drawing or spec.character_drawing
    assert (
        character_drawing
    ), f"'{spec.unique_name}' is missing CharacterDrawing."
    return StrictNpcSpec(
        unique_name=spec.unique_name,
        character_drawing=character_drawing,
        collide_with_others=spec.collide_with_others,
        avatar=spec.avatar,
        display_name=spec.display_name,
        event=spec.event,
        config=spec.config,
        cyclic_walk=spec.cyclic_walk,
    )
