from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import ClassVar, Generic, Self, TypeVar, override

from nextrpg.core.dataclass_with_default import private_init_below
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class WidgetOnScreen(Scene):
    widget_input: Widget
    name_to_on_screens: dict[str, Coordinate | AreaOnScreen]
    _: KW_ONLY = private_init_below()
    _is_selected: bool = False
    _parent: Scene | None = None

    @property
    def select(self) -> Self:
        return replace(self, _is_selected=True)

    @property
    def deselect(self) -> Self:
        return replace(self, _is_selected=False)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self._parent:
            parent = self._parent.tick(time_delta)
        else:
            parent = None
        ticked = self._tick(time_delta)
        return replace(ticked, _parent=parent)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self._parent:
            parent = self._parent.drawing_on_screens
        else:
            parent = ()
        return parent + self._drawing_on_screens

    @override
    def event(self, event: IoEvent) -> Scene:
        if not self._is_selected:
            return self
        if (
            isinstance(event, KeyPressDown)
            and event.key is KeyboardKey.CANCEL
            and self._parent
        ):
            return self._parent
        return self._event(event)

    def with_parent(self, parent: Scene) -> Self:
        return replace(self, _parent=parent)

    def _tick(self, time_delta: Millisecond) -> Self:
        return self

    @property
    @abstractmethod
    def _drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]: ...

    def _event(self, event: IoEvent) -> Scene:
        return self

    def _get_on_screen[T](self, cls: type[T]) -> T:
        name = getattr(self.widget_input, "name", None)
        assert name, f"Require 'name' attribute for widget {self.widget_input}."
        obj = self.name_to_on_screens.get(name)
        assert isinstance(
            obj, cls
        ), f"Require {cls.__name__} for {name}. Got {obj}."
        return obj


_WidgetOnScreen = TypeVar("_WidgetOnScreen", bound=WidgetOnScreen)


@dataclass(frozen=True)
class Widget(ABC, Generic[_WidgetOnScreen]):
    widget_on_screen_type: ClassVar[type]

    def widget_on_screen(
        self, name_to_on_screens: dict[str, Coordinate | AreaOnScreen]
    ) -> _WidgetOnScreen:
        return self.widget_on_screen_type(
            widget_input=self, name_to_on_screens=name_to_on_screens
        )
