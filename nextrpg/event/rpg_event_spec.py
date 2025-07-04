from typing import Any, Protocol

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.scene.map_helper import MapHelper


class RpgEventSpec(Protocol):
    def __call__(
        self,
        player: CharacterOnScreen,
        npc: CharacterOnScreen,
        map_helper: MapHelper,
        **kwargs: Any
    ) -> None: ...
