from test.util import MockCharacterDrawing, MockScene

from nextrpg import SayEventScene


def test_say() -> None:
    event = SayEventScene(
        generator=None,
        scene=MockScene(),
        character_or_scene=MockCharacterDrawing(),
        message="",
    )
    assert event._text_top_left
