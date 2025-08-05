from ast import fix_missing_locations, parse
from collections.abc import Callable
from functools import lru_cache, wraps
from inspect import getsource
from textwrap import dedent
from typing import Any, Generator

from nextrpg.global_config.global_config import config


@lru_cache
def transform[**P](
    fun: Callable[P, None],
) -> Callable[P, Generator["RpgEventScene[Any]", Any, None]]:
    src = dedent(getsource(fun))
    tree = parse(src)
    for transformer in config().event.transformers:
        tree = transformer.visit(tree)
    tree = fix_missing_locations(tree)

    code = compile(tree, __file__, "exec")
    ctx = fun.__globals__ | {
        v: c.cell_contents
        for v, c in zip(fun.__code__.co_freevars, fun.__closure__ or ())
    }
    exec(code, ctx)
    transformed = ctx[fun.__name__]
    return wraps(fun)(transformed)


def register_rpg_event[**P, R](fun: Callable[P, R]) -> Callable[P, R]:
    registered_rpg_events[fun.__name__] = fun
    return fun


registered_rpg_events: dict[str, Callable[..., None]] = {}
