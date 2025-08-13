import json
from functools import cache
from typing import TypeVar, override

from nextrpg.core.logger import Logger
from nextrpg.save.json_saveable import JsonSaveable
from nextrpg.save.save_io import SaveIo

_T = TypeVar("_T", bound=JsonSaveable)

logger = Logger()


class JsonSaveIo(SaveIo[JsonSaveable]):
    @override
    def save(self, slot: str, source: JsonSaveable) -> None:
        if (file := self.config.directory / slot).exists():
            data = json.loads(file.read_text())
        else:
            file.parent.mkdir(parents=True, exist_ok=True)
            data = {}
        logger.debug(t"Saving to {file}: {source}")
        data[_key(source)] = source.save
        file.write_text(json.dumps(data))

    @override
    def load(self, slot: str, source: _T) -> _T:
        if (file := self.config.directory / slot).exists():
            logger.debug(t"Loading save {file} for {source}")
            slot_data = json.loads(file.read_text())
            if data := slot_data.get(_key(source)):
                if res := source.load(data):
                    return res
        return source


@cache
def json_save_io() -> JsonSaveIo:
    return JsonSaveIo()


def _key(source: JsonSaveable) -> str:
    return ".".join(source.key)
