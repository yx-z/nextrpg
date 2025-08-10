from collections.abc import Callable
from typing import Any

from nextrpg.scene.scene import Scene


class EventAsAttr:
    def __getattr__(self, attr: str) -> Callable[..., Scene]:
        from nextrpg.scene.rpg_event.eventful_scene import (
            registered_rpg_event_scenes,
        )

        if event := registered_rpg_event_scenes.get(attr):
            return lambda *args, **kwargs: event(self, *args, **kwargs)

        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            raise

    def __getitem__(self, *args: Any): ...
