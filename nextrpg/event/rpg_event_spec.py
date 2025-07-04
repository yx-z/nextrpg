from typing import Any, Protocol

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npcs import Npcs


class RpgEventSpec(Protocol):
    def __call__(
        self,
        player: CharacterOnScreen,
        npc: CharacterOnScreen,
        npcs: Npcs,
        **kwargs: Any
    ) -> None: ...
