from dataclasses import dataclass, replace
from typing import Any, Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_spec import StrictNpcSpec
from nextrpg.character.player_on_screen import PlayerOnScreen


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

    def collide_start_event(self, player: PlayerOnScreen) -> bool:
        if not self.restart_event or not self.spec.event:
            return False
        if self._area_on_screen:
            return player.bottom_center in self._start_event_area_on_screen
        return self._start_event_area_on_screen.collide(
            player._start_event_area_on_screen
        )
