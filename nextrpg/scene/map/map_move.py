from dataclasses import dataclass, replace
from functools import cache
from typing import TYPE_CHECKING, Callable

from cachetools import LRUCache

from nextrpg.character.character_spec import CharacterSpec
from nextrpg.character.player_on_screen import PlayerOnScreen
from nextrpg.config.config import config
from nextrpg.core.time import Millisecond, get_timepoint
from nextrpg.scene.transition_scene import TransitionScene

if TYPE_CHECKING:
    from nextrpg.scene.map.map_scene import MapScene


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

        next_scene: MapScene | None = None
        if not (tmx := _tmxs().get(self.to_scene)):
            next_scene = self.to_scene(spec)
            tmx = str(next_scene.tmx_file)

        if timed_scene := _scenes().get(tmx):
            scene = timed_scene.scene
            player = scene.init_player(spec)
            scene_with_player = replace(scene, player=player)

            time_delta = now - timed_scene.time
            to_scene = scene_with_player.tick(time_delta)
        else:
            to_scene = next_scene or self.to_scene(spec)

        # Cache from_scene.
        _scenes()[str(from_scene.tmx_file)] = _TimedScene(now, from_scene)
        # Cache to_scene.
        _tmxs()[self.to_scene] = tmx
        return TransitionScene(to_scene)


@dataclass(frozen=True)
class _TimedScene:
    time: Millisecond
    scene: MapScene


@cache
def _scenes() -> LRUCache[str, _TimedScene]:
    return LRUCache(config().map.cache_size)


@cache
def _tmxs() -> LRUCache[
    (
        Callable[[CharacterSpec | None], MapScene]
        | Callable[[CharacterSpec], MapScene]
    ),
    str,
]:
    return LRUCache(config().map.cache_size)
