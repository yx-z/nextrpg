from nextrpg import Size


def test_dimension() -> None:
    assert Size(4, 4) / 4 == Size(2, 2)
