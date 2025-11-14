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
from nextrpg.core.cached_decorator import cached
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    private_init_below,
)
from nextrpg.core.module_and_attribute import (
    ModuleAndAttribute,
    to_module_and_attribute,
)
from nextrpg.core.util import background_thread

if TYPE_CHECKING:
    from nextrpg.config.system.save_config import SaveConfig
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


class HasSaveData[S: SaveData]:
    @property
    def save_data(self) -> S: ...


class LoadFromSave[S: SaveData](HasSaveData[S]):
    @override
    @cached_property
    def save_data(self) -> dict[str, list[str] | S]:
        cls = type(self)
        module_and_class = to_module_and_attribute(cls)
        return {
            "class": module_and_class.save_data,
            "save_data": self._save_data,
        }

    @cached_property
    def _save_data(self) -> S: ...

    @classmethod
    def load_from_save(cls, data: S) -> Self:
        save_data = data["save_data"]
        cls_str = data["class"]
        clss = ModuleAndAttribute.load_from_save(cls_str).imported
        if clss is not cls:
            return clss._load_from_save(save_data)
        return cls._load_from_save(save_data)

    @classmethod
    def _load_from_save(cls, data: S) -> Self: ...


class UpdateFromSave[S: SaveData](HasSaveData[S]):
    @override
    @cached_property
    def save_data(self) -> dict[str, list[str] | S]:
        cls = type(self)
        module_and_class = to_module_and_attribute(cls)
        return {
            "class": module_and_class.save_data,
            "save_data": self._save_data,
        }

    @property
    def _save_data(self) -> S: ...

    def update_from_save(self, data: dict[str, list[str] | S]) -> Self | None:
        save_data = data["save_data"]
        cls_str = data["class"]
        clss = ModuleAndAttribute.load_from_save(cls_str).imported
        if clss is not type(self):
            return clss._update_from_save(self, save_data)
        return self._update_from_save(save_data)

    def _update_from_save(self, data: S) -> Self | None: ...

    @property
    def _save_data(self) -> S: ...


class LoadFromSaveEnum(LoadFromSave, Enum):
    @override
    @cached_property
    def _save_data(self) -> str:
        return self.name

    @override
    @classmethod
    def _load_from_save(cls, data: str) -> Self:
        return cls[data]


class UpdateSavable[S: SaveData](UpdateFromSave[S]):
    def save_key(self) -> str:
        return type(self).__qualname__


class LoadSavable[S: SaveData](LoadFromSave[S]):
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


def save_meta(save_slot: str) -> Future[None]:
    meta_type = _create_save_slot_meta_class(save_slot)
    meta = meta_type()
    return shared_save_slot().save(meta)


def load_save_meta(save_slot: str) -> GameSaveMeta | None:
    meta_type = _create_save_slot_meta_class(save_slot)
    return shared_save_slot().load(meta_type)


@cached(lambda resource_config: resource_config.save_slot_cache_size)
@dataclass_with_default(frozen=True)
class SaveIo:
    slot: str
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

    def update[U: UpdateSavable](self, update_from_save: U) -> U:
        key = update_from_save.save_key()
        return (
            self._load(key, update_from_save.update_from_save)
            or update_from_save
        )

    def load[L: LoadSavable](self, load_from_save: type[L]) -> L | None:
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

    def _load[U: UpdateSavable, L: LoadSavable](
        self, key: str, loader: Callable[[SaveData], L | U | None]
    ) -> U | L | None:
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


def shared_save_slot() -> SaveIo:
    shared_slot = _config().shared_slot
    return SaveIo(shared_slot)


class _SaveSlotMeta(GameSaveMeta, LoadSavable):
    pass


def _create_save_slot_meta_class(
    save_slot: str,
) -> type[_SaveSlotMeta]:
    _SaveSlotMeta.save_key = classmethod(lambda _: save_slot)
    return _SaveSlotMeta
