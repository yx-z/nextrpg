import json
import sys
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from enum import Enum
from functools import cache, cached_property
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING, Any, Self, override

from nextrpg import __version__
from nextrpg.config.system.save_config import SaveConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.util import background_thread

if TYPE_CHECKING:
    from nextrpg.core.log import Log


@dataclass(frozen=True)
class AliasAndBytes:
    alias: str
    bytes: bytes


type Primitive = str | int | float | bool | None
type Json = Primitive | list["Json"] | dict[str, "Json"]
type SaveData = Primitive | AliasAndBytes | list["SaveData"] | dict[
    str, "SaveData"
]


class HasSaveData[_S: SaveData]:
    @property
    def save_data(self) -> _S: ...


class LoadFromSave[_S: SaveData](HasSaveData[_S]):
    @classmethod
    def load_from_save(cls, data: _S) -> Self: ...


class UpdateFromSave[_S: SaveData](HasSaveData[_S]):
    def update_from_save(self, data: _S) -> Self | None: ...


class LoadFromSaveEnum(LoadFromSave, Enum):
    @override
    @cached_property
    def save_data(self) -> str:
        return self.name

    @override
    @classmethod
    def load_from_save(cls, data: str) -> Self:
        return cls[data]


class UpdateSavable[_S: SaveData](UpdateFromSave[_S]):
    def save_key(self) -> str:
        return type(self).__qualname__


class LoadSavable[_S: SaveData](LoadFromSave[_S]):
    @classmethod
    def save_key(cls) -> str:
        return cls.__qualname__


@cache
def _config() -> SaveConfig:
    from nextrpg.config.config import config

    return config().save


@cache
def _log() -> Log:
    from nextrpg.core.log import Log

    return Log()


@dataclass(frozen=True)
class GameSaveMeta:
    config: SaveConfig = field(default_factory=_config)
    _: KW_ONLY = private_init_below()
    save_time: datetime = field(default_factory=datetime.now)
    nextrpg_version: str = __version__

    @cached_property
    def save_time_str(self) -> str:
        return self.save_time.strftime(self.config.time_format)

    @cached_property
    def save_data(self) -> dict[str, Any]:
        return {
            "save_time": self.save_time_str,
            "nextrpg_version": self.nextrpg_version,
        }

    @classmethod
    def load_from_save(cls, data: dict[str, Any]) -> Self:
        time_format = _config().time_format
        save_time = datetime.strptime(data["save_time"], time_format)
        nextrpg_version = data["nextrpg_version"]
        return GameSaveMeta(
            save_time=save_time, nextrpg_version=nextrpg_version
        )


def _create_save_slot_meta_class(
    save_slot: str,
) -> type[GameSaveMeta & LoadSavable]:
    class SaveSlotMeta(GameSaveMeta, LoadSavable):
        @override
        @classmethod
        def save_key(cls) -> str:
            return save_slot

    return SaveSlotMeta


def save_meta(save_slot: str) -> Future[None]:
    meta_type = _create_save_slot_meta_class(save_slot)
    meta = meta_type()
    return SaveIo().save(meta)


def load_save_meta(save_slot: str) -> GameSaveMeta | None:
    meta_type = _create_save_slot_meta_class(save_slot)
    return SaveIo().load(meta_type)


@dataclass_with_default(frozen=True)
class SaveIo:
    slot: str = default(lambda self: self.config.shared_slot)
    config: SaveConfig = field(default_factory=_config)
    _: KW_ONLY = private_init_below()
    _log: Log = field(default_factory=_log)

    def save(self, savable: UpdateSavable | LoadSavable) -> Future[None]:
        if not isinstance(savable, GameSaveMeta):
            save_meta(self.slot)
        key = savable.save_key()
        self._log.debug(t"Saving {key} at {self.slot}")
        future = background_thread().submit(self._save, savable)
        future.add_done_callback(lambda fut: self._on_save_complete(key, fut))
        return future

    def remove(self) -> None:
        rmtree(self.config.directory / self.slot, ignore_errors=True)

    def update[_U: UpdateSavable](self, update_from_save: _U) -> _U:
        key = update_from_save.save_key()
        return (
            self._load(key, update_from_save.update_from_save)
            or update_from_save
        )

    def load[_L: LoadSavable](self, load_from_save: type[_L]) -> _L | None:
        key = load_from_save.save_key()
        return self._load(key, load_from_save.load_from_save)

    @cached_property
    def web(self) -> bool:
        # TODO: Implement web save/load using IndexedDB.
        return sys.platform == "emscripten"

    def _on_save_complete(self, key, future: Future[None]) -> None:
        if exp := future.exception():
            self._log.error(t"Failed to save {key} at {self.slot}. {exp}")
            return
        self._log.debug(t"Saved {key} at {self.slot}")

    def _save(self, savable: UpdateSavable | LoadSavable) -> None:
        key = savable.save_key()
        data = self._serialize(key, savable.save_data)
        blob = self._read_text()
        blob[key] = data
        json_blob = json.dumps(blob)
        self._text_path.parent.mkdir(parents=True, exist_ok=True)
        self._text_path.write_text(json_blob)
        self._read_text.cache_clear()

    def _load[_U: UpdateSavable, _L: LoadSavable](
        self, key: str, loader: Callable[[SaveData], _L | _U | None]
    ) -> _U | _L | None:
        self._log.debug(t"Loading {key} at {self.slot}")
        if json_like := self._read_text().get(key):
            data = self._deserialize(key, json_like)
            return loader(data)
        return None

    def _write_bytes(self, key: str, alias_and_bytes: AliasAndBytes) -> None:
        file = self._key_and_alias(key, alias_and_bytes.alias)
        path = self._bytes_path(file)
        path.write_bytes(alias_and_bytes.bytes)

    def _deserialize(self, key: str, data: Json) -> SaveData:
        if isinstance(data, list):
            return [self._deserialize(key, datum) for datum in data]
        if isinstance(data, dict):
            return {
                key: self._deserialize(key, value)
                for key, value in data.items()
            }
        if (
            isinstance(data, str)
            and (
                path := self._bytes_path(self._key_and_alias(key, data))
            ).exists()
        ):
            alias = data.split(self.config.key_delimiter, maxsplit=1)[1]
            read_bytes = path.read_bytes()
            return AliasAndBytes(alias, read_bytes)
        return data

    @cache
    def _read_text(self) -> dict[str, Json]:
        if (file := self._text_path).exists():
            text = file.read_text()
            return json.loads(text)
        return {}

    def _serialize(self, key: str, data: SaveData) -> Json:
        if isinstance(data, AliasAndBytes):
            self._write_bytes(key, data)
            return self._key_and_alias(key, data)
        if isinstance(data, list):
            return [self._serialize(key, datum) for datum in data]
        if isinstance(data, dict):
            return {
                key: self._serialize(key, value) for key, value in data.items()
            }
        return data

    def _bytes_path(self, file: str) -> Path:
        return self.config.directory / self.slot / file

    @cached_property
    def _text_path(self) -> Path:
        return self.config.directory / self.slot / self.config.text_file

    def _key_and_alias(self, key: str, alias: str) -> str:
        return self.config.key_delimiter.join((key, alias))
