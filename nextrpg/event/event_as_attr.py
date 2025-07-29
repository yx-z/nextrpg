from collections.abc import Callable

from nextrpg.event.rpg_event import registered_events
from nextrpg.scene.scene import Scene


def event_as_attr[T](cls: type[T]) -> type[T]:
    def getattr(self, attr: str) -> Callable[..., Scene]:
        if event := registered_events.get(attr):
            return lambda *args, **kwargs: event(self, *args, **kwargs)
        raise AttributeError(
            f"{attr} is neither a registered RPG event nor a member of {type(self)}."
        )

    cls.__getattr__ = getattr
    return cls
