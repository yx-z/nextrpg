from collections.abc import Callable
from typing import Any

from nextrpg.event.rpg_event import registered_events
from nextrpg.scene.scene import Scene


class EventAsAttr:
    def __getattr__(self, attr: str) -> Callable[..., Scene]:
        if event := registered_events.get(attr):
            return lambda *args, **kwargs: event(self, *args, **kwargs)
        raise AttributeError(
            f"{attr} is neither a registered RPG event nor a member of {type(self)}."
        )

    def __getitem__(self, *args: Any): ...
