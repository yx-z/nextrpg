import nextrpg.config


def test_initial_config() -> None:
    nextrpg.config._initial_config = None
    assert nextrpg.config.initial_config()


def test_config() -> None:
    nextrpg.config._cfg = None
    assert nextrpg.config.config()