import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from nextrpg.audio.music_spec import MusicSpec
from nextrpg.character.npc_spec import NpcSpec
from nextrpg.character.player_spec import PlayerSpec
from nextrpg.core.module_and_attribute import ModuleAndAttribute

if TYPE_CHECKING:
    from nextrpg.map.map_move import MapMove
    from nextrpg.map.map_scene import MapScene


def _infer_creation_function() -> ModuleAndAttribute[Callable]:
    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0]).__name__
    return ModuleAndAttribute(module, frame.function)


@dataclass(frozen=True)
class MapSpec:
    tmx: str | Path
    player: PlayerSpec
    move: MapMove | tuple[MapMove, ...] = ()
    npc: NpcSpec | tuple[NpcSpec, ...] = ()
    music: MusicSpec | None = None
    creation_function: ModuleAndAttribute = field(
        default_factory=_infer_creation_function
    )

    def __call__(self, *args: Any, **kwargs: Any) -> MapScene:
        from nextrpg.map.map_scene import MapScene

        return MapScene(spec=self)
