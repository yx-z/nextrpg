from ast import fix_missing_locations, parse
from collections.abc import Callable
from functools import lru_cache
from inspect import getsource, isfunction
from textwrap import dedent
from typing import Any, Generator

from nextrpg.global_config.global_config import config


@lru_cache
def transform[**P](
    fun: Callable[P, None], name_override: str | None = None
) -> Callable[P, Generator["RpgEventScene[Any]", Any, None]]:
    if isfunction(fun):
        function = fun
        name = fun.__name__
    else:
        function = fun.__call__
        name = "__call__"

    src = dedent(getsource(function))
    tree = parse(src)
    for transformer in config().event.transformers:
        tree = transformer.visit(tree)
    tree = fix_missing_locations(tree)

    code = compile(tree, __file__, "exec")
    ctx = function.__globals__ | {
        v: c.cell_contents
        for v, c in zip(
            function.__code__.co_freevars, function.__closure__ or ()
        )
    }
    exec(code, ctx)

    transformed = ctx[name_override or name]
    if isfunction(fun):
        return transformed
    else:
        return lambda *args, **kwargs: transformed(fun, *args, **kwargs)


def register_rpg_event[**P, R](fun: Callable[P, R]) -> Callable[P, R]:
    registered_rpg_events[fun.__name__] = fun
    return fun


registered_rpg_events: dict[str, Callable[..., None]] = {}
