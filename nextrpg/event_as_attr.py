from collections.abc import Callable
from nextrpg.rpg_event import registered_events
from nextrpg.scene import Scene
from nextrpg.model import export


@export
class EventAsAttr:
    def __getattr__(self, attr: str) -> Callable[..., Scene]:
        if event := registered_events.get(attr):
            return lambda *args, **kwargs: event(self, *args, **kwargs)
        raise AttributeError(
            f"{attr} is neither a registered RPG event nor a member of {type(self)}."
        )
