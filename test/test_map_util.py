from test.util import override_config

from nextrpg import (
    Config,
    Coordinate,
    GuiConfig,
    ResizeMode,
    Size,
    center_player,
)


def test_center_player() -> None:
    assert center_player(Coordinate(0, 0), Size(1, 2)) == Coordinate(0, 0)
    assert center_player(Coordinate(800, 900), Size(200, 100)) == Coordinate(
        1080, 620
    )
    with override_config(
        Config(
            gui=GuiConfig(
                size=Size(20, 25), resize_mode=ResizeMode.KEEP_NATIVE_SIZE
            )
        )
    ):
        assert center_player(Coordinate(10, 40), Size(100, 50)) == Coordinate(
            0, -25
        )
