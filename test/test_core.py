from pytest import approx, raises

from nextrpg.core import (
    Coordinate,
    Direction,
    DirectionalOffset,
    Size,
)


def test_directional_offset() -> None:
    assert DirectionalOffset(Direction.UP, 10).direction is Direction.UP
    assert DirectionalOffset(Direction.UP, 10).offset == 10


def test_coordinate() -> None:
    assert Coordinate(10, 20) * 2 == Coordinate(20, 40)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.UP, 5
    ) == Coordinate(10, 15)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.DOWN, 5
    ) == Coordinate(10, 25)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.LEFT, 5
    ) == Coordinate(5, 20)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.RIGHT, 5
    ) == Coordinate(15, 20)
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.UP_LEFT, 10
    ) == approx(Coordinate(2.9289321881345254, 12.928932188134524))
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.UP_RIGHT, 10
    ) == approx(Coordinate(17.071067811865476, 12.928932188134524))
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.DOWN_LEFT, 10
    ) == approx(Coordinate(2.9289321881345254, 27.071067811865476))
    assert Coordinate(10, 20) + DirectionalOffset(
        Direction.DOWN_RIGHT, 10
    ) == approx(Coordinate(17.071067811865476, 27.071067811865476))
    assert Coordinate(10, 20) + Coordinate(1, 2) == Coordinate(11, 22)
    with raises(ValueError):
        coord = Coordinate(1, 2)
        coord + DirectionalOffset("INVALID_DIRECTION", 1)  # type: ignore


def test_size() -> None:
    assert Size(2, 3) * 2 == Size(4, 6)
    with raises(ValueError):
        Size(-1, -1)
