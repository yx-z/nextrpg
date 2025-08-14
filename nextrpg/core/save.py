import json
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import KW_ONLY
from functools import cache
from pathlib import Path
from shutil import rmtree
from typing import Any, Iterable, Self, TypeAlias, TypeVar

from cachetools import LRUCache

from nextrpg.core.dataclass_with_init import (
    dataclass_with_init,
    default,
    not_constructor_below,
)
from nextrpg.core.logger import Logger
from nextrpg.global_config.save_config import SaveConfig

_Primitive: TypeAlias = str | int | float | bool | None
type _Json = _Primitive | list["_Json"] | dict[str, "_Json"]
type _JsonLike = _Primitive | list["_JsonLike"] | dict[str, "SaveData"]
type SaveData = bytes | _JsonLike

logger = Logger()


class Savable[_S](ABC):
    @abstractmethod
    def save(self) -> _S: ...

    @property
    def key(self) -> tuple[str, ...]:
        return _key(self)


class UpdateFromSave[_S](Savable[_S]):
    @abstractmethod
    def update(self, data: _S) -> Self | None: ...


class LoadFromSave[_S](Savable[_S]):
    @classmethod
    @abstractmethod
    def load(cls, data: _S) -> Self: ...


_S = TypeVar("_S", bound=Savable)
_L = TypeVar("_L", bound=LoadFromSave)
_U = TypeVar("_U", bound=UpdateFromSave)


@dataclass_with_init(frozen=True)
class SaveIo:
    config: SaveConfig = default(lambda self: self._config)
    _: KW_ONLY = not_constructor_below()
    _text_data_cache: LRUCache[str, dict] = default(
        lambda self: LRUCache(self.config.cache_size)
    )

    def save[_S](self, savable: _S, slot: str | None = None) -> _S:
        key = _concat(savable.key)
        slot = slot or self.config.shared_slot
        logger.debug(t"Saving {slot=} {key=}")
        if isinstance(data := savable.save(), bytes):
            return self._write_bytes(slot, key, data)
        self._write_text(slot, key, data)
        return savable

    def remove(self, slot: str) -> None:
        self._text_data_cache.pop(slot)
        rmtree(self.config.directory / slot, ignore_errors=True)

    def update(self, arg: _U, slot: str | None = None) -> _U:
        key = _concat(arg.key)
        return self._load(key, slot, loader=arg.update, fallback=arg)

    def load(self, arg: type[_L], slot: str | None = None) -> _L | None:
        key = _concat(_key(arg))
        return self._load(key, slot, loader=arg.load, fallback=None)

    def _load(
        self,
        key: str,
        slot: str | None,
        loader: Callable[[SaveData], _L | _U],
        fallback: _U | None,
    ) -> _U | _L | None:
        slot = slot or self.config.shared_slot
        if (file := self._bytes_path(slot, key)).exists():
            return loader(file.read_bytes())
        if json_like := self._read_text(slot).get(key):
            data = self._deserialize(slot, key, json_like)
            return loader(data)
        return fallback

    @property
    def web(self) -> bool:
        return sys.platform == "emscripten"

    def _write_bytes(self, slot: str, key: str, data: bytes) -> None:
        path = self._bytes_path(slot, key)
        path.write_bytes(data)

    def _deserialize(
        self, slot: str, key: str, json_like: _JsonLike
    ) -> _JsonLike:
        if isinstance(json_like, _Primitive):
            return json_like
        if isinstance(json_like, list):
            return [
                self._deserialize(slot, _concat((key, i)), j)
                for i, j in enumerate(json_like)
            ]
        res: dict[str, SaveData] = {}
        for sub_key, value in json_like.items():
            concat_key = _concat((key, sub_key))
            if isinstance(value, str) and (
                (file := self._bytes_path(slot, concat_key)).exists()
            ):
                res[sub_key] = file.read_bytes()
            else:
                res[sub_key] = self._deserialize(slot, concat_key, value)
        return res

    def _write_text(self, slot: str, key: str, json_like: _JsonLike) -> None:
        data = self._read_text(slot)
        data[key] = self._serialize(slot, key, json_like)
        self._text_data_cache[slot] = data
        path = self._text_path(slot)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def _text_path(self, slot: str) -> Path:
        return self.config.directory / slot / self.config.text_save_file

    def _read_text(self, slot: str) -> dict[str, SaveData]:
        if res := self._text_data_cache.get(slot):
            return res
        if (file := self._text_path(slot)).exists():
            res = json.loads(file.read_text())
        else:
            res = {}
        self._text_data_cache[slot] = res
        return res

    def _serialize(self, slot: str, key: str, json_like: _JsonLike) -> _Json:
        if isinstance(json_like, _Primitive):
            return json_like
        if isinstance(json_like, list):
            return [
                self._serialize(slot, _concat((key, i)), j)
                for i, j in enumerate(json_like)
            ]
        res: dict[str, _Json] = {}
        for sub_key, value in json_like.items():
            concat_key = _concat((key, sub_key))
            if isinstance(value, bytes):
                res[sub_key] = concat_key
                self._write_bytes(slot, concat_key, value)
            else:
                res[sub_key] = self._serialize(slot, concat_key, value)
        return res

    def _bytes_path(self, slot: str, key: str) -> Path:
        return self.config.directory / slot / key

    @property
    def _config(self) -> SaveConfig:
        from nextrpg.global_config.global_config import config

        return config().save


@cache
def save_io() -> SaveIo:
    return SaveIo()


def _update(arg: _U, data: SaveData) -> _U:
    if res := arg.update(data):
        return res
    return arg


def _concat(args: Iterable[Any]) -> str:
    return "_".join(map(str, args))


def _key(x: type | Any) -> tuple[str, ...]:
    if isinstance(x, type):
        return x.__module__, x.__qualname__
    return x.__module__, x.__class__.__qualname__
