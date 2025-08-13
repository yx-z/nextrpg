from abc import abstractmethod
from typing import Self

from nextrpg.save.saveable import Saveable

type Json = None | bool | int | float | str | list["Json"] | dict[str, "Json"]


class JsonSaveable(Saveable[Json]):
    @property
    @abstractmethod
    def save(self) -> Json: ...

    @abstractmethod
    def load(self, data: Json) -> Self | None: ...
