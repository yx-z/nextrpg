from nextrpg import SayEventScene
from test.util import MockCharacterDrawing, MockScene


def test_say() -> None:
    event = SayEventScene(
        generator=None,
        scene=MockScene(),
        character_or_scene=MockCharacterDrawing(),
        message="",
    )
    assert event._text_top_left
