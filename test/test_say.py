from nextrpg.event.say_event import SayEvent
from nextrpg.scene.scene import Scene
from test.util import MockCharacterDrawing


def test_say() -> None:
    event = SayEvent(
        generator=None,
        scene=Scene(),
        character=MockCharacterDrawing(),
        message="",
    )
    assert event._coordinate
