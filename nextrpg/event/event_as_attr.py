from collections.abc import Callable
from typing import Any

from nextrpg.scene.scene import Scene


class EventAsAttr:
    def __getattr__(self, attr: str) -> Callable[..., Scene]:
        from nextrpg.event.event_scene import (
            registered_rpg_event_scenes,
        )
        from nextrpg.event.event_transformer import registered_rpg_events

        if (event := registered_rpg_event_scenes.get(attr)) or (
            event := registered_rpg_events.get(attr)
        ):
            return lambda *args, **kwargs: event(self, *args, **kwargs)
        return self.__getattribute__(attr)

    def __getitem__(self, *args: Any): ...
