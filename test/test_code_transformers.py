from textwrap import dedent
from typing import Any
from ast import fix_missing_locations, parse, unparse
from inspect import getsource
from pytest import raises
from nextrpg import ANNOTATE_SAY


def test_annotate_say() -> None:
    def fun(p: Any) -> None:
        p: "abc"
        p["hi"]: "def"

    src = getsource(fun)
    tree = parse(dedent(src))
    tree = fix_missing_locations(ANNOTATE_SAY.visit(tree))
    assert tree

    def fun2(p: Any) -> None:
        p.dict["hi"]: "def"

    src = getsource(fun2)
    tree = parse(dedent(src))
    with raises(ValueError):
        ANNOTATE_SAY.visit(tree)

    def fun3(p: Any) -> None:
        p.attr: "def"

    src = getsource(fun3)
    tree = parse(dedent(src))
    with raises(ValueError):
        ANNOTATE_SAY.visit(tree)
