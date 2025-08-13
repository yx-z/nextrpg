from abc import ABC, abstractmethod
from typing import Self


class Saveable[T](ABC):
    @abstractmethod
    def save(self) -> T: ...

    @abstractmethod
    def load(self, data: T) -> Self | None: ...
