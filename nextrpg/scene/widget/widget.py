from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import KW_ONLY, replace
from functools import cached_property
from typing import ClassVar, Generic, Self, TypeVar, override

from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
    type_name,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import tick_optional
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, is_key_press
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene


@dataclass_with_default(frozen=True)
class WidgetOnScreen(Scene):
    widget: Widget
    name_to_on_screens: dict[str, Coordinate | AreaOnScreen]
    parent: Scene | None = None
    _: KW_ONLY = private_init_below()
    _is_selected: bool = False
    _enter_animation: TimedAnimationOnScreens | None = default(
        lambda self: self._init_enter_animation
    )
    _exit_animation: TimedAnimationOnScreens | None = None

    @override
    def __str__(self) -> str:
        return f"{type_name(self)}({self.widget})"

    @property
    def select(self) -> Self:
        return replace(self, _is_selected=True)

    @property
    def deselect(self) -> Self:
        return replace(self, _is_selected=False)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        parent = tick_optional(self.parent, time_delta)
        ticked = self._tick_after_parent(time_delta)
        if (
            enter_animation := tick_optional(self._enter_animation, time_delta)
        ) and enter_animation.is_complete:
            enter_animation = None
        if (
            exit_animation := tick_optional(self._exit_animation, time_delta)
        ) and exit_animation.is_complete:
            return parent
        return replace(
            ticked,
            parent=parent,
            _enter_animation=enter_animation,
            _exit_animation=exit_animation,
        )

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self.parent:
            parent = self.parent.drawing_on_screens
        else:
            parent = ()
        if self._enter_animation:
            return parent + self._enter_animation.drawing_on_screens
        if self._exit_animation:
            return parent + self._exit_animation.drawing_on_screens
        return parent + self._drawing_on_screens_after_parent

    @override
    def event(self, event: IoEvent) -> Scene:
        if (
            not self._is_selected
            or self._enter_animation
            or self._exit_animation
        ):
            return self
        if is_key_press(event, KeyboardKey.CANCEL):
            return self._exit
        return self._event_after_selected(event)

    def from_on_screen[T](self, cls: type[T]) -> T:
        name = getattr(self.widget, "name", None)
        assert (
            name
        ), f"Require 'name' attribute for widget fetching on-screen Coordinate/AreaOnScreen: {self.widget}."
        obj = self.name_to_on_screens.get(name)
        assert isinstance(
            obj, cls
        ), f"Require {cls.__name__} for widget {name}. Got {obj}."
        return obj

    def with_parent(self, parent: Scene | None) -> Self:
        return replace(self, parent=parent)

    def _tick_after_parent(self, time_delta: Millisecond) -> Self:
        return self

    @property
    @abstractmethod
    def _drawing_on_screens_after_parent(
        self,
    ) -> tuple[DrawingOnScreen, ...]: ...

    def _event_after_selected(self, event: IoEvent) -> Scene:
        return self

    @property
    def _init_enter_animation(self) -> TimedAnimationOnScreens | None:
        if self.widget.enter_animation:
            return self.widget.enter_animation(
                self._drawing_on_screens_after_parent
            )
        return None

    @property
    def _init_exit_animation(self) -> TimedAnimationOnScreens | None:
        if self.widget.exit_animation:
            return self.widget.exit_animation(
                self._drawing_on_screens_after_parent
            )
        return None

    @cached_property
    def _exit(self) -> Scene:
        if not self.parent:
            return self
        if self.widget.exit_animation:
            exit_animation = self.widget.exit_animation(
                self._drawing_on_screens_after_parent
            )
            return replace(self, _exit_animation=exit_animation)
        return self.parent


_WidgetOnScreen = TypeVar("_WidgetOnScreen", bound=WidgetOnScreen)


@dataclass_with_default(frozen=True)
class Widget(ABC, Generic[_WidgetOnScreen]):
    widget_on_screen_type: ClassVar[type]
    enter_animation: (
        Callable[[tuple[DrawingOnScreen, ...]], TimedAnimationOnScreens] | None
    ) = None
    exit_animation: (
        Callable[[tuple[DrawingOnScreen, ...]], TimedAnimationOnScreens] | None
    ) = default(lambda self: self._init_exit_animation)

    @property
    def _init_exit_animation(
        self,
    ) -> Callable[[DrawingOnScreen, ...], TimedAnimationOnScreens] | None:
        if self.enter_animation:

            def exit_animation(
                d: tuple[DrawingOnScreen, ...],
            ) -> TimedAnimationOnScreens:
                return self.enter_animation(d).reverse

            return exit_animation
        return None

    def widget_on_screen(
        self,
        name_to_on_screens: dict[str, Coordinate | AreaOnScreen],
        parent: Scene | None,
    ) -> _WidgetOnScreen:
        return self.widget_on_screen_type(
            widget=self,
            name_to_on_screens=name_to_on_screens,
            parent=parent,
        )
