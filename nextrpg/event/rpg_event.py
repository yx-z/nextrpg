from collections.abc import Callable


def register_rpg_event[R, **P](fun: Callable[P, R]) -> Callable[P, R]:
    registered_events[fun.__name__] = fun
    return fun


registered_events: dict[str, Callable[..., None]] = {}
