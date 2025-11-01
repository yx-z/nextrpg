from dataclasses import dataclass, replace
from functools import cache
from typing import TYPE_CHECKING, Callable

from cachetools import LRUCache

from nextrpg.character.character_spec import CharacterSpec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config.config import config
from nextrpg.core.save import ModuleAndAttribute, module_and_attribute
from nextrpg.core.time import Millisecond, get_timepoint
from nextrpg.scene.transition_scene import TransitionScene

if TYPE_CHECKING:
    from nextrpg.map.map_scene import MapScene


@dataclass(frozen=True)
class MapMove:
    to_object: str
    from_object: str
    to_scene: (
        Callable[[CharacterSpec | None], MapScene]
        | Callable[[CharacterSpec], MapScene]
    )

    def move_to_scene(
        self, from_scene: MapScene, player: PlayerOnScreen
    ) -> TransitionScene:
        spec = replace(
            player.spec, unique_name=self.to_object, character=player.character
        )
        now = get_timepoint()

        to_scene_name = module_and_attribute(self.to_scene)
        if timed_scene := _scenes().get(to_scene_name):
            scene = timed_scene.scene
            player = scene.init_player(spec)
            scene_with_player = replace(scene, player=player)

            time_delta = now - timed_scene.time
            to_scene = scene_with_player.tick_without_event(time_delta)
        else:
            to_scene = self.to_scene(spec)

        _scenes()[from_scene.creation_function] = _TimedScene(now, from_scene)
        _scenes()[to_scene.creation_function] = _TimedScene(now, to_scene)
        return TransitionScene(to_scene)


@dataclass(frozen=True)
class _TimedScene:
    time: Millisecond
    scene: MapScene


@cache
def _scenes() -> LRUCache[ModuleAndAttribute, _TimedScene]:
    return LRUCache(config().map.cache_size)
