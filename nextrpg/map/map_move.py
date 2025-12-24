from dataclasses import dataclass, replace
from functools import cache
from typing import TYPE_CHECKING, Callable

from cachetools import LRUCache

from nextrpg.audio.music import stop_music
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.player_spec import PlayerSpec
from nextrpg.config.config import config
from nextrpg.core.module_and_attribute import (
    ModuleAndAttribute,
    to_module_and_attribute,
)
from nextrpg.core.time import Millisecond, get_timepoint
from nextrpg.game.game_state import GameState
from nextrpg.map.map_spec import MapSpec
from nextrpg.scene.transition_scene import TransitionScene

if TYPE_CHECKING:
    from nextrpg.map.map_scene import MapScene


@dataclass(frozen=True)
class MapMove:
    to_object: str
    from_object: str
    to_map: Callable[[PlayerSpec, GameState], MapSpec]

    def __call__(
        self, from_map: MapScene, player: PlayerOnScreen, state: GameState
    ) -> tuple[TransitionScene, GameState]:
        player_spec = player.spec.to_map(
            self.to_object, player.character_drawing
        )
        now = get_timepoint()

        to_map_function = to_module_and_attribute(self.to_map)
        if time_and_map := _maps().get(to_map_function):
            scene = time_and_map.map
            player = scene.init_player(player_spec)
            scene_with_player = replace(scene, player=player)

            time_delta = now - time_and_map.time
            to_map, state = scene_with_player.tick_without_event(
                time_delta, state
            )
            map_spec = to_map.spec
        else:
            map_spec = self.to_map(player_spec, state)
            # Don't load to_map given it'll block the game loop.
            # Loaded asynchronously during TransitionScene intermediary period.
            to_map = map_spec
        if not map_spec.music:
            stop_music()

        map_scenes = _maps()
        time_and_map = _TimeAndMap(now, from_map)
        map_scenes[from_map.spec.creation_function] = time_and_map

        scene = TransitionScene(to_map)
        return scene, state


@dataclass(frozen=True)
class _TimeAndMap:
    time: Millisecond
    map: MapScene


@cache
def _maps() -> LRUCache[ModuleAndAttribute, _TimeAndMap]:
    size = config().system.resource.map_scene_cache_size
    return LRUCache(size)
