import logging
from collections.abc import Callable, Hashable
from dataclasses import dataclass, fields, is_dataclass
from typing import TYPE_CHECKING, Any

from cachetools import LRUCache

if TYPE_CHECKING:
    from nextrpg.config.system.resource_config import ResourceConfig

console_logger = logging.getLogger("cache")


def key_by_first_arg[K: Hashable](cls: type, *args: Any, **kwargs: Any) -> K:
    if args:
        return args[0]
    assert is_dataclass(
        cls
    ), f"Expect a dataclass to infer first argument as key. Got {cls}"
    all_fields = fields(cls)
    assert all_fields, f"Expect dataclass with fields. Got {cls}."
    return kwargs.get(all_fields[0].name)


@dataclass(frozen=True)
class cached[T, K, **P]:
    size_function: Callable[[ResourceConfig], int]
    create_key: Callable[type, P, K | None] = key_by_first_arg

    def __call__[Type: type](self, cls: Type) -> Type:

        def new(klass: type[T], *args: P.args, **kwargs: P.kwargs) -> T:
            if not (instances := getattr(klass, "_nextrpg_instances", None)):
                from nextrpg.config.config import config

                size = self.size_function(config().system.resource)
                instances = LRUCache(size)
                klass._nextrpg_instances = instances

            if klass is not cls:
                return object.__new__(klass)

            if (key := self.create_key(klass, *args, **kwargs)) is None:
                return object.__new__(klass)

            if (instance := instances.get(key)) is not None:
                return instance

            instance = object.__new__(klass)
            instances[key] = instance
            if len(instances) == instances.maxsize:
                console_logger.debug(
                    f"Cache for {klass} is full with size {len(instances)}."
                )
            return instance

        cls.__new__ = new
        return cls
