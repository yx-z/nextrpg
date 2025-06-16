from dataclasses import dataclass

from nextrpg.util import clone, partition


def test_partition() -> None:
    odd, even = partition(range(5), lambda x: x % 2 == 1)
    assert odd == [1, 3]
    assert even == [0, 2, 4]


def test_clone() -> None:
    @dataclass(frozen=True)
    class Data:
        i: int
        _j: str = "abc"

    assert clone(Data(1), _j="def") == Data(1, "def")
    assert clone(Data(2)) == Data(2, "abc")
