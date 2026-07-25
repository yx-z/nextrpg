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


class EventTransformError(RuntimeError):
    """Raised when an event function cannot be source-transformed.

    The dialogue DSL (@cutscene / registered RPG events) works by reading the
    function's Python source and rewriting its AST. This requires a function
    defined in a .py file with accessible source. Common causes of failure:
    lambdas, functions defined in a REPL / via eval / exec, decorators that
    hide the original function, or source-less (frozen) deployments.
    """


def transform_event[**P](
    fun: Callable[P, None], name_override: str | None = None
) -> Callable[P, Generator[EventScene, Any, None]]:
    if isfunction(fun):
        function = fun
        name = fun.__name__
    else:
        function = fun.__call__
        name = "__call__"

    try:
        src = dedent(getsource(function))
        tree = parse(src)
    except (OSError, TypeError, ValueError) as e:
        raise EventTransformError(
            f"Cannot read source for {fun!r} to apply the nextrpg event "
            f"transformer. The dialogue DSL requires a function defined in a "
            f".py file with accessible source; lambdas, REPL/eval-defined "
            f"functions, or source-less deployments are not supported. "
            f"Either define the event as a normal function, or use the "
            f"explicit non-macro form (call say()/yield directly). "
            f"Original error: {e}"
        ) from e

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
