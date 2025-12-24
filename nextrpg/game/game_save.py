from collections.abc import Callable
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Self, override

from nextrpg.character.player_spec import PlayerSpec
from nextrpg.core.module_and_attribute import (
    ModuleAndAttribute,
    to_module_and_attribute,
)
from nextrpg.core.save import LoadSavable
from nextrpg.game.game_state import GameState
from nextrpg.map.map_scene import MapScene


@dataclass(frozen=True)
class GameSave(LoadSavable):
    player_creation: Callable[[], PlayerSpec]
    state: GameState
    scene: MapScene

    @override
    @cached_property
    def save_data_this_class(self) -> dict[str, Any]:
        scene_creation = self.scene.spec.creation_function
        player = to_module_and_attribute(self.player_creation)
        return {
            "scene": self.scene.save_data,
            "player_creation": player.save_data,
            "scene_creation": scene_creation.save_data,
            "state": self.state.save_data,
        }

    @override
    @classmethod
    def load_this_class_from_save(cls, data: dict[str, Any]) -> Self:
        scene_creation = ModuleAndAttribute.load_from_save(
            data["scene_creation"]
        )
        player_creation = ModuleAndAttribute.load_from_save(
            data["player_creation"]
        )

        player = player_creation.imported()
        state = GameState.load_from_save(data["state"])
        map_spec = scene_creation.imported(player, state)
        map_scene = map_spec()
        saved_scene = map_scene.update_from_save(data["scene"])
        return cls(
            player_creation=player_creation, scene=saved_scene, state=state
        )
