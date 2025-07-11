from collections.abc import Callable


def register_rpg_event[R, **P](fun: Callable[P, R]) -> Callable[P, R]:
    """
    Mark a function as an event handler.

    Arguments:
        `fun`: Function with a unique name that handles
            player/NPC interaction.

    Returns:
        `Callable`: The original function.
    """
    if fun.__name__ in registered_events:
        raise ValueError(f"Event {fun.__name__} already registered.")
    registered_events[fun.__name__] = fun
    return fun


registered_events: dict[str, Callable[..., None]] = {}
