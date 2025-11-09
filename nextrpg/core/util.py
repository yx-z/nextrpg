from concurrent.futures.thread import ThreadPoolExecutor
from functools import cache
from typing import Any, NoReturn


def throw(message: str) -> NoReturn:
    raise RuntimeError(message)


def type_name(obj: Any | type) -> str:
    if isinstance(obj, type):
        cls = obj
    else:
        cls = type(obj)
    return cls.__name__


@cache
def background_thread() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(max_workers=1)
