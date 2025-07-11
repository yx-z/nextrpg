from nextrpg.event.rpg_event import register_rpg_event


@register_rpg_event
def say(character, message: str) -> None:
    """
    Character says a message.

    Arguments:
        `character`: The character to say something.

        `message`: The message to say.

    Returns:
        Type-hinted type: `None`. For user code (RpgEventSpec), `say` returns
            no result (from the ` SayEvent ` scene).
        Actual type: `RpgEventCallable`. For `Npcs`/`MapScene` to yield the
            scene coroutine.
    """
    from nextrpg.event.say import SayEvent

    return lambda generator, scene: SayEvent(
        generator, scene, character, message
    )
