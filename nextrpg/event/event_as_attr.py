from collections.abc import Callable
from nextrpg.event.rpg_event import registered_events
from nextrpg.scene.scene import Scene
from nextrpg.model import NEXTRPG_INSTANCE_INIT


class EventAsAttr:
    def __getattr__(self, attr: str) -> Callable[..., Scene] | None:
        if event := registered_events.get(attr):
            return lambda *args, **kwargs: event(self, *args, **kwargs)
        if attr == NEXTRPG_INSTANCE_INIT:
            return None
        raise AttributeError(
            f"{attr} is neither a registered RPG event nor a member of {self}."
        )
