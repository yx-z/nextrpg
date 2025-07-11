from dataclasses import replace

from nextrpg.character.moving_npc import MovingNpcOnScreen
from nextrpg.character.npcs import NpcSpec
from nextrpg.draw.coordinate import Coordinate
from nextrpg.core import Size
from nextrpg.draw.draw_on_screen import Rectangle
from test.util import MockCharacterDrawing


def test_moving_npc_on_screen() -> None:
    npc = MovingNpcOnScreen(
        coordinate=Coordinate(0, 0),
        spec=NpcSpec(
            name="name",
            character=MockCharacterDrawing(),
            event=lambda *_: None,
            idle_duration=10,
            move_duration=10,
        ),
        path=Rectangle(Coordinate(0, 0), Size(10, 10)),
        collisions=(),
    )
    assert npc.tick(1).tick(1).moving
    assert npc.tick(11).tick(20).moving
    assert npc.move(0) == Coordinate(0, 0)
    assert replace(npc, _event_triggered=True).tick(0)
