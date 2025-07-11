from nextrpg.draw.coordinate import Coordinate
from nextrpg.draw.draw_on_screen import Polygon
from nextrpg.walk import Walk


def test_walk() -> None:
    w = Walk(
        path=Polygon(
            (Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1)), closed=False
        ),
        move_speed=1,
        cyclic=False,
    )
    assert w.reset.coordinate == Coordinate(0, 0)
    assert w.tick(100).tick(2000).tick(20000)
    assert w.tick(0).tick(1).tick(10).tick(100)

    assert not Walk(
        path=Polygon((Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1))),
        move_speed=1,
        cyclic=False,
    ).completed

    w2 = Walk(
        path=Polygon(
            (Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1)), closed=False
        ),
        move_speed=1,
        cyclic=False,
    )
