from test.util import MockCharacterDraw

from nextrpg import CharacterSpec, Coordinate, PlayerOnScreen


def test_character_on_screen() -> None:
    assert MockCharacterDraw().display_name
    assert MockCharacterDraw().coordinate
    assert PlayerOnScreen(
        spec=CharacterSpec(object_name="abc", character=MockCharacterDraw()),
        coordinate=Coordinate(0, 0),
        collisions=(),
    ).display_name
