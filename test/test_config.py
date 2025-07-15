import nextrpg


def test_initial_config() -> None:
    nextrpg._initial_config = None
    assert nextrpg.initial_config()
    assert nextrpg.initial_config()


def test_config() -> None:
    nextrpg.config._cfg = None
    assert nextrpg.config()
