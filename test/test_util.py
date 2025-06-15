from nextrpg.util import partition


def test_partition() -> None:
    odd, even = partition(range(5), lambda x: x % 2 == 1)
    assert odd == [1, 3]
    assert even == [0, 2, 4]
