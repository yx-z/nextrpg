"""
RPG event registration system for `NextRPG`.

This module provides a decorator-based event registration system for RPG-style
interactions. It allows functions to be marked as event handlers that can be
triggered by player or NPC interactions.

The RPG event system features:
- Function decorator for event registration
- Unique event name validation
- Global event registry
- Integration with player/NPC interaction systems
"""

from collections.abc import Callable

from nextrpg.model import export


@export
def register_rpg_event[R, **P](fun: Callable[P, R]) -> Callable[P, R]:
    """
    Mark a function as an event handler.

    This decorator registers a function as an RPG event handler that can be
    triggered by player or NPC interactions. Each event must have a unique
    function name.

    Arguments:
        `fun`: Function with a unique name that handles player/NPC interaction.

    Returns:
        `Callable`: The original function.

    Raises:
        `ValueError`: If an event with the same name is already registered.
    """
    if fun.__name__ in registered_events:
        raise ValueError(f"Event {fun.__name__} already registered.")
    registered_events[fun.__name__] = fun
    return fun


registered_events: dict[str, Callable[..., None]] = {}
"""
Global registry of registered RPG events.

This dictionary stores all registered event handlers, mapping function names to
their corresponding callable functions.
"""
