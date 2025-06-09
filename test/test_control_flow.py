from nextrpg.util import assert_not_none, partition


def test_assert_not_none() -> None:
    x: int | None = 12
    assert assert_not_none(x) == 12


def test_partition() -> None:
    odd, even = partition(range(5), lambda x: x % 2 == 1)
    assert odd == [1, 3]
    assert even == [0, 2, 4]
