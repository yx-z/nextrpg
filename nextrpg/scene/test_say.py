from nextrpg.event.say import SayEvent
from nextrpg.scene.scene import Scene
from test.util import MockCharacterDrawing


def test_say() -> None:
    event = SayEvent(
        _generator=None,
        _scene=Scene(),
        character=MockCharacterDrawing(),
        message="",
    )
    assert event._coordinate
