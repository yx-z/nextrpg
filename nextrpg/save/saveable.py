from abc import ABC, abstractmethod
from typing import Self


class Saveable[T](ABC):
    @property
    @abstractmethod
    def save(self) -> T: ...

    @abstractmethod
    def load(self, data: T) -> Self | None: ...

    @property
    def key(self) -> tuple[str, ...]:
        return self.__module__, self.__class__.__qualname__
