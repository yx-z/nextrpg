"""
Event attribute system for `nextrpg`.

This module provides a proxy class that allows RPG events to be accessed as
attributes on scenes and other objects. It includes the `EventAsAttr` class
which dynamically resolves event names to registered event handlers.

Features:
    - Dynamic event resolution
    - Attribute-style event access
    - Integration with registered events
    - Error handling for missing events
"""

from collections.abc import Callable

from nextrpg.model import export
from nextrpg.rpg_event import registered_events
from nextrpg.scene import Scene


@export
class EventAsAttr:
    """
    Proxy class for accessing RPG events as attributes.

    This class provides a dynamic attribute interface for accessing registered
    RPG events. When an attribute is accessed, it looks up the corresponding
    event in the registered events dictionary and returns a callable that can be
    invoked.
    """

    def __getattr__(self, attr: str) -> Callable[..., Scene]:
        """
        Get an event handler as an attribute.

        Looks up the given attribute name in the registered events and returns a
        callable that can be invoked with arguments.

        Arguments:
            attr: The name of the event to look up.

        Returns:
            A callable that invokes the registered event with the current object
            as the first argument.

        Raises:
            AttributeError: If the attribute is not a registered RPG event.
        """
        if event := registered_events.get(attr):
            return lambda *args, **kwargs: event(self, *args, **kwargs)
        raise AttributeError(
            f"{attr} is neither a registered RPG event nor a member of {type(self)}."
        )
