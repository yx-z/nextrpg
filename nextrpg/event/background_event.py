from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Self

from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen

if TYPE_CHECKING:
    from nextrpg.scene.rpg_event.eventful_scene import EventfulScene


@dataclass(frozen=True)
class BackgroundEventSentinel:
    cls: type


@dataclass_with_default(frozen=True)
class BackgroundEvent(ABC):
    _: KW_ONLY = private_init_below()
    sentinel: BackgroundEventSentinel = default(
        lambda self: BackgroundEventSentinel(type(self))
    )

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return ()

    def apply(self, scene: EventfulScene) -> EventfulScene:
        return scene

    @abstractmethod
    def tick(self, time_delta: Millisecond) -> Self: ...

    @property
    @abstractmethod
    def is_complete(self) -> bool: ...
