from collections.abc import Iterable
from dataclasses import dataclass, replace
from functools import cached_property
from typing import Any, Self, override

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.character.npc_spec import StrictNpcSpec
from nextrpg.character.player_on_screen import PlayerOnScreen


@dataclass(frozen=True, kw_only=True)
class NpcOnScreen(CharacterOnScreen):
    spec: StrictNpcSpec
    restart_event: bool = True

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        return super().save_data_this_class | {
            "restart_event": self.restart_event,
            "spec": self.spec.save_data,
        }

    @override
    def update_this_class_from_save(self, data: dict[str, Any]) -> Self:
        character = super().update_this_class_from_save(data)
        restart_event = data["restart_event"]
        spec = self.spec.update_from_save(data["spec"])
        return replace(character, restart_event=restart_event, spec=spec)

    def collide_start_event(self, player: PlayerOnScreen) -> bool:
        if not self.restart_event or not self.spec.event:
            return False
        if self._area_on_screen:
            return player.bottom_center in self._start_event_area_on_screen
        return self._start_event_area_on_screen.collide(
            player._start_event_area_on_screen
        )


def replace_npc(
    npcs: Iterable[NpcOnScreen], updated: NpcOnScreen
) -> tuple[NpcOnScreen, ...]:
    return tuple(updated if n.has_same_name(updated) else n for n in npcs)
