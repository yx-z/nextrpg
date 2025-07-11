from ast import fix_missing_locations, parse
from inspect import getsource
from textwrap import dedent
from types import CodeType
from typing import Callable

from nextrpg.config import config


def transform_event[R, **P](fun: Callable[P, R]) -> CodeType:
    src = dedent(getsource(fun))
    tree = parse(src)
    for transformer in config().event.transformers:
        tree = transformer.visit(tree)
    return compile(fix_missing_locations(tree), f"<{__file__}>", "exec")
