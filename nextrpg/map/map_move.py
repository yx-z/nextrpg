from dataclasses import dataclass, replace
from functools import cache
from typing import TYPE_CHECKING, Callable

from cachetools import LRUCache

from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.character.player_spec import PlayerSpec
from nextrpg.config.config import config
from nextrpg.core.module_and_attribute import (
    ModuleAndAttribute,
    to_module_and_attribute,
)
from nextrpg.core.time import Millisecond, get_timepoint
from nextrpg.scene.transition_scene import TransitionScene

if TYPE_CHECKING:
    from nextrpg.map.map_scene import MapScene


@dataclass(frozen=True)
class MapMove:
    to_object: str
    from_object: str
    to_scene: Callable[[PlayerSpec], MapScene]

    def move_to_scene(
        self, from_scene: MapScene, player: PlayerOnScreen
    ) -> TransitionScene:
        spec = player.spec.to_map(self.to_object, player.character_drawing)
        now = get_timepoint()

        to_scene_name = to_module_and_attribute(self.to_scene)
        if timed_scene := _map_scenes().get(to_scene_name):
            scene = timed_scene.scene
            player = scene.init_player(spec)
            scene_with_player = replace(scene, player=player)

            time_delta = now - timed_scene.time
            to_scene = scene_with_player.tick_without_event(time_delta)
        else:
            # Don't load to_scene given it'll block the game loop.
            # Loaded asynchronously during TransitionScene intermediary period.
            to_scene = lambda: self.to_scene(spec)

        map_scenes = _map_scenes()
        timed_scene = _TimedScene(now, from_scene.stop_sound())
        map_scenes[from_scene.creation_function] = timed_scene

        return TransitionScene(to_scene)


@dataclass(frozen=True)
class _TimedScene:
    time: Millisecond
    scene: MapScene


@cache
def _map_scenes() -> LRUCache[ModuleAndAttribute, _TimedScene]:
    return LRUCache(config().resource.map_scene_cache_size)
