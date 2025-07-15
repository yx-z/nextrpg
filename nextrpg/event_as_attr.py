"""
Event attribute system for NextRPG.

This module provides a proxy class that allows RPG events to be
accessed as attributes on scenes and other objects. It includes
the `EventAsAttr` class which dynamically resolves event names
to registered event handlers.

The event attribute system features:
- Dynamic event resolution
- Attribute-style event access
- Integration with registered events
- Error handling for missing events

Example:
    ```python
    from nextrpg.event_as_attr import EventAsAttr
    from nextrpg.scene import Scene

    # Create event proxy
    event_proxy = EventAsAttr()

    # Access events as attributes
    event_proxy.say("Hello, World!")
    event_proxy.open_door()
    ```
"""

from collections.abc import Callable

from nextrpg.model import export
from nextrpg.rpg_event import registered_events
from nextrpg.scene import Scene


@export
class EventAsAttr:
    """
    Proxy class for accessing RPG events as attributes.

    This class provides a dynamic attribute interface for accessing
    registered RPG events. When an attribute is accessed, it looks
    up the corresponding event in the registered events dictionary
    and returns a callable that can be invoked.

    Example:
        ```python
        from nextrpg.event_as_attr import EventAsAttr

        # Create event proxy
        event_proxy = EventAsAttr()

        # Access events as attributes
        event_proxy.say("Hello, World!")
        event_proxy.open_chest()
        ```
    """

    def __getattr__(self, attr: str) -> Callable[..., Scene]:
        """
        Get an event handler as an attribute.

        Looks up the given attribute name in the registered events
        and returns a callable that can be invoked with arguments.

        Arguments:
            `attr`: The name of the event to look up.

        Returns:
            `Callable[..., Scene]`: A callable that invokes the
                registered event with the current object as the
                first argument.

        Raises:
            `AttributeError`: If the attribute is not a registered
                RPG event.

        Example:
            ```python
            # Access event as attribute
            say_handler = event_proxy.say
            say_handler("Hello, World!")
            ```
        """
        if event := registered_events.get(attr):
            return lambda *args, **kwargs: event(self, *args, **kwargs)
        raise AttributeError(
            f"{attr} is neither a registered RPG event nor a member of {type(self)}."
        )
