from dataclasses import dataclass, replace
from typing import Any, Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_spec import StrictNpcSpec


@dataclass(frozen=True, kw_only=True)
class NpcOnScreen(CharacterOnScreen):
    spec: StrictNpcSpec
    restart_event: bool = True

    @override
    @property
    def save_data(self) -> dict[str, Any]:
        return super().save_data | {"restart_event": self.restart_event}

    @override
    def update_from_save(self, save: dict[str, Any]) -> Self:
        character = super().update_from_save(save)
        restart_event = save["restart_event"]
        return replace(character, restart_event=restart_event)
