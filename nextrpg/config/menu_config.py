from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nextrpg.scene.map.map_scene import MapScene
    from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class MenuConfig:
    create: Callable[[MapScene], Scene] | None = None
    blur_radius: int = 2
