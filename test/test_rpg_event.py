from ast import parse

from pytest import raises

from nextrpg.event.rpg_event import _yield, register_rpg_event


def test_register_rpg_event() -> None:
    @register_rpg_event
    def fun():
        pass

    assert not fun()

    with raises(ValueError):
        register_rpg_event(fun)


def test_yield_events() -> None:
    assert _yield.visit(parse("""def fun():\n  print()"""))
