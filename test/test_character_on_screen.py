from test.util import MockCharacterDrawing

from nextrpg import CharacterSpec, Coordinate, PlayerOnScreen


def test_character_on_screen() -> None:
    assert PlayerOnScreen(
        spec=CharacterSpec(object_name="abc", character=MockCharacterDrawing()),
        coordinate=Coordinate(0, 0),
        collisions=(),
    ).name
