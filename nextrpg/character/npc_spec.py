from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.character.character_spec import CharacterSpec, _BaseCharacterSpec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.polygon_character_drawing import PolygonCharacterDrawing
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.draw.color import Color
from nextrpg.event.event_transformer import transform

if TYPE_CHECKING:
    from nextrpg.character.npc_on_screen import NpcOnScreen
    from nextrpg.scene.rpg_event.rpg_event_scene import (
        EventfulScene,
        EventGenerator,
    )


type EventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, EventfulScene]
type RpgEvent = Callable[[*EventSpecParams], EventGenerator] | Callable[
    [*EventSpecParams], bool
] | Callable[[*EventSpecParams], None]


class NpcEventStartMode(Enum):
    CONFIRM = auto()
    COLLIDE = auto()


@dataclass_with_default(frozen=True)
class EventSpec:
    event: RpgEvent
    start_mode: NpcEventStartMode = NpcEventStartMode.CONFIRM
    _: KW_ONLY = private_init_below()
    generator: EventGenerator = default(lambda self: transform(self.event))


@dataclass_with_default(frozen=True, kw_only=True)
class NpcSpec(_BaseCharacterSpec):
    character: CharacterDrawing | Color | None = None
    event: EventSpec | RpgEvent | None = None
    cyclic_walk: bool = True
    collide_with_others: bool = default(
        lambda self: isinstance(self.character, CharacterDrawing)
        and not isinstance(self.character, PolygonCharacterDrawing)
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
