from nextrpg.character.npc_spec import MovingNpcSpec, NpcSpec
from nextrpg.core import Size
from nextrpg.draw_on_screen import Coordinate, Rectangle
from test.util import MockCharacterDrawing


def test_npc_spec() -> None:
    assert NpcSpec(
        name="abc",
        character=MockCharacterDrawing(),
        event_spec=lambda *_: None,
    ).put_on_screen(Coordinate(0, 1)).coordinate == Coordinate(0, 1)


def test_moving_npc_spec() -> None:
    assert (
        not MovingNpcSpec(
            name="abc",
            character=MockCharacterDrawing(),
            event_spec=lambda *_: None,
        )
        .put_moving_on_screen(
            Coordinate(0, 0), Rectangle(Coordinate(0, 0), Size(1, 1)), []
        )
        .collisions
    )
