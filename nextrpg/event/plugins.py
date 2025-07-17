"""
Plugin system for `NextRPG`.

This module provides plugin functions that extend the functionality of
`NextRPG` games. It includes event handlers and utility functions that can be
registered and used throughout the game framework.

The plugin system features:
- Event registration and handling
- Character and scene interaction
- Message display functionality
- Integration with RPG event system
"""

from typing import Any

from nextrpg.character.character_on_screen import CharacterOnScreen
from nextrpg.core.coordinate import Coordinate
from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.scene.scene import Scene


@register_rpg_event
def say(
    character_or_scene: CharacterOnScreen | Scene,
    message: str,
    arg: Coordinate | None = None,
    **kwargs: Any
) -> None:
    """
    Display a message from a character or scene using a say event.

    This function creates a say event that displays a message from a character
    or scene. It is registered as an RPG event and can be used in event scripts.

    Arguments:
        `character_or_scene`: The character or scene that will say the message.
        `message`: The message to say.
        `arg`: Optional coordinate argument for positioning. Defaults to `None`.
        `**kwargs`: Additional keyword arguments passed to the say event.

    Returns:
        `None`: For user code (`RpgEventSpec`), `say` returns no result (from
        the `SayEvent` scene). For `Npcs`/`MapScene` to yield the scene
        coroutine, it returns an `RpgEventCallable`.
    """
    from nextrpg.scene.say_event_scene import SayEventScene

    return lambda generator, scene: SayEventScene(
        generator=generator,
        scene=scene,
        character_or_scene=character_or_scene,
        message=message,
        arg=arg,
        **kwargs
    )
