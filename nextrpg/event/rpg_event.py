from collections.abc import Callable
from typing import Any


def register_rpg_event[**P](fun: Callable[P, Any]) -> Callable[P, None]:
    registered_events[fun.__name__] = fun
    return fun


registered_events: dict[str, Callable[..., None]] = {}
