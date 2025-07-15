import nextrpg


def test_initial_config() -> None:
    nextrpg.global_config._initial_config = None
    assert nextrpg.global_config.initial_config()
    assert nextrpg.global_config.initial_config()


def test_config() -> None:
    nextrpg.global_config._cfg = None
    assert nextrpg.global_config.config()
