from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, field

from nextrpg.character.character_on_screen import (
    CharacterOnScreen,
    CharacterSpec,
)
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.dataclass_with_instance_init import (
    dataclass_with_instance_init,
    instance_init,
    not_constructor_below,
)
from nextrpg.event.event_transformer import transform
from nextrpg.global_config.character_config import CharacterConfig
from nextrpg.global_config.global_config import config

type NpcEventSpecParams = tuple[PlayerOnScreen, NpcOnScreen, "EventfulScene"]
type NpcEventSpec = Callable[[*NpcEventSpecParams], "EventGenerator | None"]


@dataclass_with_instance_init(frozen=True)
class NpcSpec(CharacterSpec):
    event: NpcEventSpec | None = None
    config: CharacterConfig = field(default_factory=lambda: config().character)
    cyclic_walk: bool = True
    _: KW_ONLY = not_constructor_below()
    generator: Callable[[*NpcEventSpecParams], "EventGenerator"] | None = (
        instance_init(
            lambda self: transform(self.event) if self.event else None
        )
    )


@dataclass(frozen=True, kw_only=True)
class NpcOnScreen(CharacterOnScreen):
    spec: NpcSpec
