from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from typing import TYPE_CHECKING, Self

from nextrpg.core.dataclass_with_default_init import (
    dataclass_with_default_init,
    default_init,
    not_constructor_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen

if TYPE_CHECKING:
    from nextrpg.scene.rpg_event.eventful_scene import EventfulScene


@dataclass(frozen=True)
class BackgroundEventSentinel:
    cls: type


@dataclass_with_default_init(frozen=True)
class BackgroundEvent(ABC):
    _: KW_ONLY = not_constructor_below()
    sentinel: BackgroundEventSentinel = default_init(
        lambda self: BackgroundEventSentinel(type(self))
    )

    @property
    def draw_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return ()

    def apply(self, scene: EventfulScene) -> EventfulScene:
        return scene

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def complete(self) -> bool: ...
