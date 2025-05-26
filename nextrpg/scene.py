from typing import Protocol

from nextrpg.common_types import Millesecond
from nextrpg.drawable import Drawable
from nextrpg.event import Event


class Scene(Protocol):
    def event(self, event: Event) -> None: ...

    def draw(self, time_delta: Millesecond) -> list[Drawable]: ...
