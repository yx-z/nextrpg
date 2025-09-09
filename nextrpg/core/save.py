import json
import sys
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import KW_ONLY, field
from enum import Enum
from functools import cache
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING, Any, Self, TypeAlias, TypeVar, override

from nextrpg import __version__
from nextrpg.config.save_config import SaveConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)

if TYPE_CHECKING:
    from nextrpg.core.log import Log

_Primitive: TypeAlias = str | int | float | bool | None
type _Json = _Primitive | list["_Json"] | dict[str, "_Json"]
type SaveData = _Primitive | bytes | list["SaveData"] | dict[str, "SaveData"]


class _Savable[_S]:
    @property
    def save_data(self) -> _S: ...


class UpdateFromSave[_S](_Savable[_S]):
    def update_from_save(self, data: _S) -> Self | None: ...

    @property
    def save_key(self) -> str:
        return module_and_class(self)


class LoadFromSave[_S](_Savable[_S]):
    @classmethod
    def save_key(cls) -> str:
        return module_and_class(cls)

    @classmethod
    def load_from_save(cls, data: _S) -> Self: ...


class LoadFromSaveEnum(LoadFromSave[str], Enum):
    @override
    @property
    def save_data(self) -> str:
        return self.name

    @override
    @classmethod
    def load_from_save(cls, data: str) -> Self:
        return cls[data]


_L = TypeVar("_L", bound=LoadFromSave)
_U = TypeVar("_U", bound=UpdateFromSave)


def _config() -> SaveConfig:
    from nextrpg.config.config import config

    return config().save


@cache
def _log() -> Log:
    from nextrpg.core.log import Log

    return Log()


@dataclass_with_default(frozen=True)
class SaveIo:
    config: SaveConfig = field(default_factory=_config)
    slot: str = default(lambda self: self.config.shared_slot)
    _: KW_ONLY = private_init_below()
    _log: Log = field(default_factory=_log)
    _thread = ThreadPoolExecutor(max_workers=1)

    def save(self, savable: _U | _L) -> Future:
        if isinstance(savable, UpdateFromSave):
            key = concat_save_key(savable.save_key)
        else:
            key = concat_save_key(savable.save_key())

        future = self._thread.submit(self._save, key, savable.save_data)
        future.add_done_callback(
            lambda _: self._log.debug(t"Saved {key} at {self.slot}")
        )
        return future

    def _save(self, key: str, data: SaveData) -> None:
        self._log.debug(t"Saving {key} at {self.slot}")
        if isinstance(data, bytes):
            self._write_bytes(key, data)
            return
        self._write_text(key, data)

    def remove(self) -> None:
        rmtree(self.config.directory / self.slot, ignore_errors=True)

    def update(self, arg: _U) -> _U:
        return self._load(
            arg.save_key, loader=arg.update_from_save, fallback=arg
        )

    def load(self, arg: type[_L]) -> _L | None:
        key = concat_save_key(arg.save_key())
        return self._load(key, loader=arg.load_from_save, fallback=None)

    @property
    def web(self) -> bool:
        # TODO: Implement web save/load using IndexedDB.
        return sys.platform == "emscripten"

    def _load(
        self,
        key: str,
        loader: Callable[[SaveData], _L | _U],
        fallback: _U | None,
    ) -> _U | _L | None:
        self._log.debug(t"Loading {key} at {self.slot}")
        if (file := self._bytes_path(key)).exists():
            return loader(file.read_bytes())
        if json_like := self._read_text().get(key):
            data = self._deserialize(key, json_like)
            return loader(data)
        return fallback

    def _write_bytes(self, key: str, data: bytes) -> None:
        path = self._bytes_path(key)
        path.write_bytes(data)

    def _deserialize(self, key: str, data: SaveData) -> SaveData:
        if isinstance(data, str) and (file := self._bytes_path(data)).exists():
            return file.read_bytes()
        if isinstance(data, _Primitive):
            return data
        if isinstance(data, list):
            return [
                self._deserialize(concat_save_key(key, i), j)
                for i, j in enumerate(data)
            ]
        return {
            sub_key: self._deserialize(concat_save_key(key, sub_key), value)
            for sub_key, value in data.items()
        }

    def _write_text(self, key: str, data: SaveData) -> None:
        data = self._serialize(key, data)
        self._text_path.parent.mkdir(parents=True, exist_ok=True)
        blob = self._read_text()
        blob[key] = data
        json_blob = json.dumps(blob)
        self._text_path.write_text(json_blob)
        self._read_text.cache_clear()

    @cache
    def _read_text(self) -> dict[str, SaveData]:
        if (file := self._text_path).exists():
            text = file.read_text()
            # Load save data, including a previously stored nextrpg version.
            return json.loads(text)
        # Create the first-time save data: store the current nextrpg version.
        return {"_nextrpg_version": __version__}

    def _serialize(self, key: str, data: SaveData) -> _Json:
        if isinstance(data, bytes):
            self._write_bytes(key, data)
            return key
        if isinstance(data, _Primitive):
            return data
        if isinstance(data, list):
            return [
                self._serialize(concat_save_key(key, index), datum)
                for index, datum in enumerate(data)
            ]
        return {
            sub_key: self._serialize(concat_save_key(key, sub_key), value)
            for sub_key, value in data.items()
        }

    def _bytes_path(self, key: str) -> Path:
        return self.config.directory / self.slot / key

    @property
    def _text_path(self) -> Path:
        return self.config.directory / self.slot / self.config.text_save_file


def _update(arg: _U, data: SaveData) -> _U:
    if res := arg.update_from_save(data):
        return res
    return arg


def module_and_class(x: type | Any) -> str:
    if isinstance(x, type):
        return concat_save_key(x.__module__, x.__qualname__)
    return concat_save_key(x.__module__, x.__class__.__qualname__)


def concat_save_key(*args: Any) -> str:
    return _config().key_delimiter.join(map(str, args))
