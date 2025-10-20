from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from nextrpg.core.time import Millisecond

if TYPE_CHECKING:
    from nextrpg.map.map_scene import MapScene
    from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class MenuConfig:
    create: Callable[[MapScene], Scene] | None = None
    blur_radius: int = 2
    fade_duration_override: Millisecond | None = None

    @property
    def fade_duration(self) -> Millisecond:
        from nextrpg.config.config import config

        if self.fade_duration_override is not None:
            return self.fade_duration_override
        return config().timing.animation_duration
