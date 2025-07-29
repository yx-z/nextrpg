from ast import parse

from pytest import raises

from nextrpg import ADD_YIELD, register_rpg_event


def test_register_rpg_event() -> None:
    @register_rpg_event
    def fun():
        pass

    assert not fun()


def test_yield_events() -> None:
    assert ADD_YIELD.visit(parse("""def fun():\n  print()"""))
