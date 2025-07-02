from unittest.mock import Mock

from nextrpg.core import Direction, DirectionalOffset, Font, Size


def test_directional_offset() -> None:
    assert DirectionalOffset(Direction.UP, 10).direction is Direction.UP
    assert DirectionalOffset(Direction.UP, 10).offset == 10


def test_size() -> None:
    assert Size(2, 3).scale(2) == Size(4, 6)
    assert f"{Size(2, 3)}" == "(2, 3)"


def test_font() -> None:
    font = Font(12)
    object.__setattr__(font, "pygame", Mock())
    font.pygame.size = Mock(return_value=(10, 20))
    assert font.text_size("123") == Size(10, 20)
