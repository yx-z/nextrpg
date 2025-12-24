import json
import logging
import sys
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import KW_ONLY, field
from enum import Enum
from functools import cache, cached_property
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING, Any, Self, overload, override

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
    from nextrpg.core.logger import Logger
    from nextrpg.game.game_save_meta import GameSaveMeta


type Primitive = str | int | float | bool | None
type Json = Primitive | list["Json"] | dict[str, "Json"]
type SaveData = Primitive | bytes | list["SaveData"] | dict[str, "SaveData"]

console_logger = logging.getLogger("save")


class HasSaveData[S: SaveData]:
    @property
    def save_data(self) -> S: ...


class LoadFromSave[S: SaveData](HasSaveData[S]):
    @override
    @cached_property
    def save_data(self) -> dict[str, tuple[str, ...] | S]:
        cls = type(self)
        module_and_class = to_module_and_attribute(cls)
        return {
            "class": module_and_class.save_data,
            "save_data": self.save_data_this_class,
        }

    @property
    def save_data_this_class(self) -> S: ...

    @classmethod
    def load_from_save(cls, data: dict[str, list[str] | S]) -> Self:
        save_data = data["save_data"]
        cls_str = data["class"]
        clss: type[Self] = ModuleAndAttribute.load_from_save(cls_str).imported
        if clss is not cls:
            return clss.load_this_class_from_save(save_data)
        return cls.load_this_class_from_save(save_data)

    @classmethod
    def load_this_class_from_save(cls, data: S) -> Self: ...


class UpdateFromSave[S: SaveData](HasSaveData[S]):
    @override
    @cached_property
    def save_data(self) -> dict[str, tuple[str, ...] | S]:
        cls = type(self)
        module_and_class = to_module_and_attribute(cls)
        return {
            "class": module_and_class.save_data,
            "save_data": self.save_data_this_class,
        }

    @property
    def save_data_this_class(self) -> S: ...

    def update_from_save(self, data: dict[str, list[str] | S]) -> Self | None:
        save_data = data["save_data"]
        cls_str = data["class"]
        clss = ModuleAndAttribute.load_from_save(cls_str).imported
        if clss is not type(self):
            return clss.update_this_class_from_save(self, save_data)
        return self.update_this_class_from_save(save_data)

    def update_this_class_from_save(self, data: S) -> Self | None: ...


class LoadFromSaveEnum(LoadFromSave, Enum):
    @override
    @cached_property
    def save_data_this_class(self) -> str:
        return self.name

    @override
    @classmethod
    def load_this_class_from_save(cls, data: str) -> Self:
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

    return config().system.save


@cache
def _get_on_screen_logger() -> Logger:
    from nextrpg.core.logger import Logger

    return Logger("save")


@cached(lambda resource_config: resource_config.save_slot_cache_size)
@dataclass_with_default(frozen=True)
class SaveIo:
    slot: str = field(default_factory=lambda: _config().shared_slot)
    config: SaveConfig = field(default_factory=_config)
    _: KW_ONLY = private_init_below()
    _on_screen_logger: Logger = field(default_factory=_get_on_screen_logger)

    def save(
        self, savable: UpdateSavable | LoadSavable | GameSaveMeta
    ) -> Future[None]:
        key = savable.save_key()
        self._on_screen_logger.debug(
            f"Saving {key=} at slot={self.slot}", console_logger
        )
        future = background_thread().submit(self._save, savable)
        future.add_done_callback(lambda fut: self._on_save_complete(key, fut))
        return future

    def remove(self) -> Self:
        rmtree(self.config.directory / self.slot, ignore_errors=True)
        self._read_text.cache_clear()
        return self

    def update[U: UpdateSavable](self, update_from_save: U) -> U:
        key = update_from_save.save_key()
        res = self._load(key, update_from_save.update_from_save)
        return res or update_from_save

    @overload
    def load[L: LoadSavable](self, load_from_save: type[L]) -> L | None: ...

    @overload
    def load(
        self, load_from_save: type[GameSaveMeta]
    ) -> GameSaveMeta | None: ...

    def load[L: LoadSavable](
        self, load_from_save: type[L | GameSaveMeta]
    ) -> L | GameSaveMeta | None:
        from nextrpg.game.game_save_meta import GameSaveMeta

        if issubclass(load_from_save, GameSaveMeta):
            return SaveIo()._load(self.slot, load_from_save.load_from_save)
        key = load_from_save.save_key()
        return self._load(key, load_from_save.load_from_save)

    @cached_property
    def web(self) -> bool:
        # TODO: Implement web save/load using IndexedDB.
        return sys.platform == "emscripten"

    def _on_save_complete(self, key: str, future: Future[None]) -> None:
        try:
            future.result()
            self._on_screen_logger.debug(
                f"Saved {key} at {self.slot}", console_logger
            )
        except Exception as exp:
            self._on_screen_logger.error(
                f"Failed to save {key} at {self.slot}: {exp}", console_logger
            )

    def _save(
        self, savable: UpdateSavable | LoadSavable | GameSaveMeta
    ) -> None:
        from nextrpg.game.game_save_meta import GameSaveMeta

        key = savable.save_key()
        blob = self._read_text()
        blob[key] = self._serialize(key, savable.save_data)
        json_blob = json.dumps(blob)
        self._text_path.parent.mkdir(parents=True, exist_ok=True)
        self._text_path.write_text(json_blob)
        self._read_text.cache_clear()
        if not isinstance(savable, GameSaveMeta):
            meta = GameSaveMeta(self.slot)
            SaveIo().save(meta).result()

    def _load[U: UpdateSavable, L: LoadSavable](
        self, key: str, loader: Callable[[SaveData], L | U | None]
    ) -> U | L | None:
        if json_like := self._read_text().get(key):
            self._on_screen_logger.debug(
                f"Loading {key=} at slot={self.slot}", console_logger
            )
            data = self._deserialize(key, json_like)
            return loader(data)
        return None

    def _write_bytes(self, key: str, data: bytes) -> None:
        path = self._bytes_path(key)
        path.write_bytes(data)

    def _deserialize(self, key: str, data: Json) -> SaveData:
        if isinstance(data, list):
            return [
                self._deserialize(self._concat(key, i), datum)
                for i, datum in enumerate(data)
            ]
        if isinstance(data, dict):
            return {
                dict_key: self._deserialize(self._concat(key, dict_key), value)
                for dict_key, value in data.items()
            }
        if isinstance(data, str) and (path := self._bytes_path(key)).exists():
            return path.read_bytes()
        return data

    @cache
    def _read_text(self) -> dict[str, Json]:
        if (file := self._text_path).exists():
            text = file.read_text()
            return json.loads(text)
        return {}

    def _serialize(self, key: str, data: SaveData) -> Json:
        if isinstance(data, bytes):
            self._write_bytes(key, data)
            return key
        if isinstance(data, list):
            return [
                self._serialize(self._concat(key, i), datum)
                for i, datum in enumerate(data)
            ]
        if isinstance(data, dict):
            return {
                dict_key: self._serialize(self._concat(key, dict_key), value)
                for dict_key, value in data.items()
            }
        return data

    def _bytes_path(self, file: str) -> Path:
        return self.config.directory / self.slot / file

    @cached_property
    def _text_path(self) -> Path:
        return self.config.directory / self.slot / self.config.text_file

    def _concat(self, k1: Any, k2: Any) -> str:
        return f"{k1}{self.config.key_delimiter}{k2}"
