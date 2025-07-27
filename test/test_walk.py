from nextrpg import Coordinate, PolygonOnScreen, Walk


def test_walk() -> None:
    w = Walk(
        path=PolygonOnScreen(
            (Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1)), closed=False
        ),
        move_speed=1,
        cyclic=False,
    )
    assert w.reset.coordinate == Coordinate(0, 0)
    assert w.tick(100).tick(2000).tick(20000)
    assert w.tick(0).tick(1).tick(10).tick(100)

    ww = Walk(
        path=PolygonOnScreen(
            (Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1))
        ),
        move_speed=1,
        cyclic=False,
    )
    assert not ww.complete
    assert ww.tick(99999).direction

    w2 = Walk(
        path=PolygonOnScreen(
            (Coordinate(0, 0), Coordinate(1, 0), Coordinate(0, 1)), closed=False
        ),
        move_speed=1,
        cyclic=False,
    )
    assert w2.tick(99999).direction
    assert w2.tick(100000).complete

    w3 = Walk(
        path=PolygonOnScreen(
            (
                Coordinate(0, 0),
                Coordinate(1, 0),
                Coordinate(1, 1),
                Coordinate(0, 1),
            )
        ),
        move_speed=1,
        cyclic=True,
    )
    assert w3.tick(1).tick(1).tick(1)
