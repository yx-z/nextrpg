from pytest import raises

from nextrpg.event.rpg_event import register_rpg_event


def test_register_rpg_event() -> None:
    @register_rpg_event
    def fun():
        pass

    assert not fun()

    with raises(ValueError):
        register_rpg_event(fun)
