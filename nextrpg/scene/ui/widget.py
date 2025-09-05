from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from enum import Enum, auto
from functools import cached_property
from typing import ClassVar, Generic, Self, TypeVar, override

from nextrpg import AnimationOnScreen
from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene


class WidgetOnScreenState(Enum):
    ENTERING = auto()
    ON_SCREEN = auto()
    EXITING = auto()


@dataclass(frozen=True)
class WidgetOnScreen(Scene):
    widget_input: Widget
    name_to_on_screens: dict[str, Coordinate | AreaOnScreen]
    parent: Scene | None = None
    _: KW_ONLY = private_init_below()
    _is_selected: bool = False
    _state: WidgetOnScreenState = WidgetOnScreenState.ON_SCREEN
    _animation: AnimationOnScreen | None = None

    @property
    def enter(self) -> Self:
        return replace(self, _state=WidgetOnScreenState.ENTERING)

    @property
    def exit(self) -> Self:
        return replace(self, _state=WidgetOnScreenState.EXITING)

    @property
    def select(self) -> Self:
        return replace(self, _is_selected=True)

    @property
    def deselect(self) -> Self:
        return replace(self, _is_selected=False)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self.parent:
            parent = self.parent.tick(time_delta)
        else:
            parent = None
        ticked = self.tick_after_parent(time_delta)
        return replace(ticked, parent=parent)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self.parent:
            parent = self.parent.drawing_on_screens
        else:
            parent = ()
        return parent + self.drawing_on_screens_after_parent

    @override
    def event(self, event: IoEvent) -> Scene:
        if not self._is_selected:
            return self
        if (
            isinstance(event, KeyPressDown)
            and event.key is KeyboardKey.CANCEL
            and self.parent
        ):
            return self.parent
        return self.event_after_selected(event)

    def tick_after_parent(self, time_delta: Millisecond) -> Self:
        return self

    @property
    @abstractmethod
    def drawing_on_screens_after_parent(
        self,
    ) -> tuple[DrawingOnScreen, ...]: ...

    def event_after_selected(self, event: IoEvent) -> Scene:
        return self

    def from_on_screen[T](self, cls: type[T]) -> T:
        name = getattr(self.widget_input, "name", None)
        assert name, f"Require 'name' attribute for widget {self.widget_input}."
        obj = self.name_to_on_screens.get(name)
        assert isinstance(
            obj, cls
        ), f"Require {cls.__name__} for {name}. Got {obj}."
        return obj

    def with_parent(self, parent: Scene | None) -> Self:
        return replace(self, parent=parent)


_WidgetOnScreen = TypeVar("_WidgetOnScreen", bound=WidgetOnScreen)


@dataclass(frozen=True)
class Widget(ABC, Generic[_WidgetOnScreen]):
    widget_on_screen_type: ClassVar[type]
    entering_animation: (
        Callable[[tuple[DrawingOnScreen, ...]], AnimationOnScreen] | None
    ) = None
    exiting_animation: (
        Callable[[tuple[DrawingOnScreen, ...]], AnimationOnScreen] | None
    ) = None

    def widget_on_screen(
        self,
        name_to_on_screens: dict[str, Coordinate | AreaOnScreen],
        parent: Scene | None,
    ) -> _WidgetOnScreen:
        return self.widget_on_screen_type(
            widget_input=self,
            name_to_on_screens=name_to_on_screens,
            parent=parent,
        )
