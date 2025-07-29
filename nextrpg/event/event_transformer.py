from ast import fix_missing_locations, parse
from inspect import getsource
from textwrap import dedent
from types import CodeType
from collections.abc import Callable

from nextrpg.global_config.global_config import config


def transform_and_compile(fun: Callable) -> CodeType:
    src = dedent(getsource(fun))
    tree = parse(src)
    for transformer in config().event.transformers:
        tree = transformer.visit(tree)
    return compile(fix_missing_locations(tree), __file__, "exec")
