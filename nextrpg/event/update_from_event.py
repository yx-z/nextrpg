from dataclasses import dataclass, replace
from typing import Self, override

from nextrpg.character.npc_on_screen import NpcOnScreen, replace_npc
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.core.time import Millisecond
from nextrpg.event.event_scene import (
    EventScene,
    register_rpg_event_scene,
)
from nextrpg.event.eventful_scene import EventfulScene
from nextrpg.game.game_state import GameState
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class UpdateFromEvent(EventScene):
    update: PlayerOnScreen | NpcOnScreen | EventfulScene | GameState

    @override
    def _tick_after_parent(
        self, time_delta: Millisecond, ticked: Self, state: GameState
    ) -> tuple[Scene, GameState]:
        match ticked.update:
            case GameState() as state:
                scene = ticked.parent
            case EventfulScene() as scene:
                pass
            case PlayerOnScreen() as player:
                scene = replace(ticked.parent, player=player)
            case NpcOnScreen() as npc:
                npcs = replace_npc(ticked.parent.npcs, npc)
                scene = replace(ticked.parent, npcs=npcs)
            case other:
                raise ValueError(
                    f"Expect PlayerOnScreen, NpcOnScreen, or EventfulScene. Got {other}"
                )
        completed = scene.complete()
        return completed, state


@register_rpg_event_scene(UpdateFromEvent)
def update_from_event(
    update: PlayerOnScreen | NpcOnScreen | EventfulScene | GameState,
) -> None: ...
