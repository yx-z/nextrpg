import logging
from ast import fix_missing_locations, parse, unparse
from collections.abc import Callable
from inspect import getsource, isfunction
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Generator

from nextrpg.config.config import config

if TYPE_CHECKING:
    from nextrpg.event.event_scene import EventScene

logger = logging.getLogger("event_transformer")


def transform_event[**P](
    fun: Callable[P, None], name_override: str | None = None
) -> Callable[P, Generator[EventScene, Any, None]]:
    if isfunction(fun):
        function = fun
        name = fun.__name__
    else:
        function = fun.__call__
        name = "__call__"

    src = dedent(getsource(function))
    tree = parse(src)
    for transformer in config().event.event_transformer.transformers:
        tree = transformer.visit(tree)
    tree = fix_missing_locations(tree)
    logger.debug(f"Parsed code for {fun}\n{unparse(tree)}")
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
