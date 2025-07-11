from ast import parse

from pytest import raises

from nextrpg.event.rpg_event import register_rpg_event
from nextrpg.event.code_transformers import ADD_YIELD


def test_register_rpg_event() -> None:
    @register_rpg_event
    def fun():
        pass

    assert not fun()

    with raises(ValueError):
        register_rpg_event(fun)


def test_yield_events() -> None:
    assert ADD_YIELD.visit(parse("""def fun():\n  print()"""))
