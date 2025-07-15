from typing import Any

from nextrpg.character_on_screen import CharacterOnScreen
from nextrpg.scene import Scene
from nextrpg.coordinate import Coordinate
from nextrpg.rpg_event import register_rpg_event
from nextrpg.model import export


@export
@register_rpg_event
def say(
    character_or_scene: CharacterOnScreen | Scene,
    message: str,
    arg: Coordinate | None = None,
    **kwargs: Any
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
    from nextrpg.say_event import SayEvent

    return lambda generator, scene: SayEvent(
        generator=generator,
        scene=scene,
        character_or_scene=character_or_scene,
        message=message,
        arg=arg,
        **kwargs
    )
