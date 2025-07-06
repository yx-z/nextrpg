from _pytest.python_api import approx

from nextrpg.coordinate import Coordinate
from nextrpg.core import Direction, DirectionalOffset


def test_coordinate() -> None:
    assert Coordinate(10, 20).shift(
        DirectionalOffset(Direction.UP, 5)
    ) == Coordinate(10, 15)
    assert Coordinate(10, 20).shift(
        DirectionalOffset(Direction.DOWN, 5)
    ) == Coordinate(10, 25)
    assert Coordinate(10, 20).shift(
        DirectionalOffset(Direction.LEFT, 5)
    ) == Coordinate(5, 20)
    assert Coordinate(10, 20).shift(
        DirectionalOffset(Direction.RIGHT, 5)
    ) == Coordinate(15, 20)
    assert Coordinate(10, 20).shift(
        DirectionalOffset(Direction.UP_LEFT, 10)
    ) == approx(Coordinate(2.9289321881345254, 12.928932188134524))
    assert Coordinate(10, 20).shift(
        DirectionalOffset(Direction.UP_RIGHT, 10)
    ) == approx(Coordinate(17.071067811865476, 12.928932188134524))
    assert Coordinate(10, 20).shift(
        DirectionalOffset(Direction.DOWN_LEFT, 10)
    ) == approx(Coordinate(2.9289321881345254, 27.071067811865476))
    assert Coordinate(10, 20).shift(
        DirectionalOffset(Direction.DOWN_RIGHT, 10)
    ) == approx(Coordinate(17.071067811865476, 27.071067811865476))
    assert Coordinate(10, 20).shift(Coordinate(1, 2)) == Coordinate(11, 22)
    assert not Coordinate(10, 20).shift(DirectionalOffset("invalid", 1))
