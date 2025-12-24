from collections.abc import Generator
from concurrent.futures.thread import ThreadPoolExecutor
from functools import cache
from typing import Any


def type_name(obj: Any | type) -> str:
    if isinstance(obj, type):
        cls = obj
    else:
        cls = type(obj)
    return cls.__name__


@cache
def background_thread() -> ThreadPoolExecutor:
    from nextrpg.config.config import config

    num_workers = config().system.resource.background_thread_count
    return ThreadPoolExecutor(max_workers=num_workers)


def generator_name(gen: Generator) -> str:
    gi_code = getattr(gen, "gi_code", None)
    return getattr(gi_code, "co_name", type(gen).__name__)


type Percentage = float
