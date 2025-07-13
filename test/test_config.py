import nextrpg.config


def test_initial_config() -> None:
    nextrpg.config.config._initial_config = None
    assert nextrpg.config.config.initial_config()
    assert nextrpg.config.config.initial_config()


def test_config() -> None:
    nextrpg.config.config._cfg = None
    assert nextrpg.config.config.config()
