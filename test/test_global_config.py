import nextrpg.global_config.global_config as mod


def test_initial_config() -> None:
    mod._initial_config = None
    assert mod.initial_config()
    assert mod.initial_config()


def test_config() -> None:
    mod._cfg = None
    assert mod.config()
