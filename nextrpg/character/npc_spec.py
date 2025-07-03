from dataclasses import dataclass, field

from nextrpg.character.character_drawing import CharacterDrawing
from nextrpg.config import config
from nextrpg.core import Millisecond, PixelPerMillisecond


@dataclass
class StaticNpcSpec:
    name: str
    drawing: CharacterDrawing


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
