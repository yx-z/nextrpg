from dataclasses import dataclass, field
from enum import Enum, auto

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config import config
from nextrpg.core import Millisecond, PixelPerMillisecond
from nextrpg.event.rpg_event_spec import RpgEventSpec


class NpcTriggerMode(Enum):
    CONFIRM_KEY = auto()
    PLAYER_COLLIDES_NPC = auto()
    NRC_COLLIDES_PLAYER = auto()


@dataclass
class StaticNpcSpec:
    name: str
    drawing: CharacterDrawing
    event_spec: RpgEventSpec
    trigger_mode: NpcTriggerMode = NpcTriggerMode.CONFIRM_KEY


@dataclass
class MovingNpcSpec(StaticNpcSpec):
    move_speed: PixelPerMillisecond = field(
        default_factory=lambda: config().character.move_speed
    )
    idle_duration: Millisecond = field(
        default_factory=lambda: config().character.idle_duration
    )
    move_duration: Millisecond = field(
        default_factory=lambda: config().character.move_duration
    )
    observe_collisions: bool = True
