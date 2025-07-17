from nextrpg import SayEventScene, Scene
from test.util import MockCharacterDrawing


def test_say() -> None:
    event = SayEventScene(
        generator=None,
        scene=Scene(),
        character_or_scene=MockCharacterDrawing(),
        message="",
    )
    assert event._text_top_left
