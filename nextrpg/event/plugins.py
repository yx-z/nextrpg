from typing import Any

from nextrpg.event.rpg_event import register_rpg_event


@register_rpg_event
def say(
    character_or_scene: CharacterOnScreen | Scene, message: str, arg: Any = None
) -> None:
    """
    Character says a message.

    Arguments:
        `message`: The message to say.

    Returns:
        Type-hinted type: `None`. For user code (RpgEventSpec), `say` returns
            no result (from the ` SayEvent ` scene).
        Actual type: `RpgEventCallable`. For `Npcs`/`MapScene` to yield the
            scene coroutine.
    """
    from nextrpg.event.say_event import SayEvent

    return lambda generator, scene: SayEvent(
        generator, scene, character_or_scene, message, arg
    )
