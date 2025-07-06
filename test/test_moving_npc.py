from nextrpg.character.moving_npc import MovingNpcOnScreen, MovingNpcSpec
from nextrpg.coordinate import Coordinate
from nextrpg.core import Size
from nextrpg.draw_on_screen import Rectangle
from test.util import MockCharacterDrawing


def test_moving_npc_on_screen() -> None:
    npc = MovingNpcOnScreen(
        coordinate=Coordinate(0, 0),
        spec=MovingNpcSpec(
            "name",
            MockCharacterDrawing(),
            lambda *_: None,
            idle_duration=10,
            move_duration=10,
        ),
        path=Rectangle(Coordinate(0, 0), Size(10, 10)),
        collisions=[],
    )
    assert not npc.tick(0).moving
    assert not npc.tick(5).tick(1).moving
    assert npc.tick(11).tick(9).moving
    assert not npc.tick(11).tick(20).moving
    assert npc.move(0) == Coordinate(0, 0)
