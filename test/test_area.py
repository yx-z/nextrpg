from nextrpg import (
    bottom_left_screen,
    bottom_right_screen,
    bottom_screen,
    left_screen,
    right_screen,
    screen,
    top_left_screen,
    top_right_screen,
    top_screen,
)


def test_area() -> None:
    assert screen()
    assert left_screen()
    assert right_screen()
    assert top_screen()
    assert top_left_screen()
    assert top_right_screen()
    assert bottom_screen()
    assert bottom_left_screen()
    assert bottom_right_screen()
