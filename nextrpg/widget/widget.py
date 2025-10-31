from abc import ABC, abstractmethod
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import ClassVar, Self, override

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.animation.timed_animation_spec import TimedAnimationSpec
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
    parent: Scene | None = field(default=None, repr=False)
    _: KW_ONLY = private_init_below()
    _is_selected: bool = False
    _enter_animation: TimedAnimationOnScreens | None = default(
        lambda self: self._init_enter_animation
    )
    _exit_animation: TimedAnimationOnScreens | None = None
    _tick_parent: bool = True

    @override
    def __str__(self) -> str:
        return f"{type_name(self)}({self.widget})"

    @cached_property
    def select(self) -> Self:
        return replace(self, _is_selected=True)

    @cached_property
    def deselect(self) -> Self:
        return replace(self, _is_selected=False)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self._tick_parent:
            parent = tick_optional(self.parent, time_delta)
        else:
            parent = self.parent
        if ticked := self._tick_without_parent(time_delta):
            return replace(ticked, parent=parent)
        return parent

    def _tick_without_parent(self, time_delta: Millisecond) -> Self | None:
        # Entering.
        if self._enter_animation:
            if (
                enter_animation := self._enter_animation.tick(time_delta)
            ) and enter_animation.is_complete:
                enter_animation = None
            return replace(self, _enter_animation=enter_animation)

        # In widget.
        if not self._exit_animation:
            return self._tick_without_parent_and_animation(time_delta)

        # Exiting.
        if (
            exit_animation := self._exit_animation.tick(time_delta)
        ) and exit_animation.is_complete:
            return None
        return replace(self, _exit_animation=exit_animation)

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self.parent:
            parent_drawing_on_screens = self.parent.drawing_on_screens
        else:
            parent_drawing_on_screens = ()
        return (
            parent_drawing_on_screens + self._drawing_on_screens_without_parent
        )

    @override
    def event(self, event: IoEvent) -> Scene:
        # Entering.
        if self._enter_animation:
            return self

        # In widget.
        if not self._exit_animation:
            if not self._is_selected:
                return self
            if is_key_press(event, KeyboardKey.CANCEL):
                return self._try_exit
            return self._event_after_selected(event)

        # Exiting.
        return self

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

    @cached_property
    def _drawing_on_screens_without_parent(
        self,
    ) -> tuple[DrawingOnScreen, ...]:
        # Entering.
        if self._enter_animation:
            return self._enter_animation.drawing_on_screens

        # In widget.
        if not self._exit_animation:
            return self._drawing_on_screens_without_parent_and_animation

        # Exiting.
        return self._exit_animation.drawing_on_screens

    def _tick_without_parent_and_animation(
        self, time_delta: Millisecond
    ) -> Self:
        return self

    @property
    @abstractmethod
    def _drawing_on_screens_without_parent_and_animation(
        self,
    ) -> tuple[DrawingOnScreen, ...]: ...

    def _event_after_selected(self, event: IoEvent) -> Scene:
        return self

    @property
    def _init_enter_animation(self) -> AnimationOnScreens | None:
        if self.widget.enter_animation:
            return self.widget.enter_animation.animate(
                self._drawing_on_screens_without_parent_and_animation
            )
        return None

    @property
    def _init_exit_animation(self) -> AnimationOnScreens | None:
        if self.widget.exit_animation:
            return self.widget.exit_animation.animate(
                self._drawing_on_screens_without_parent_and_animation
            )
        return None

    @cached_property
    def _try_exit(self) -> Scene:
        if not self.parent:
            return self
        if exit_animation := self._init_exit_animation:
            return replace(self, _exit_animation=exit_animation)
        return self.parent


@dataclass_with_default(frozen=True)
class Widget(ABC):
    # Must be a subclass of WidgetOnScreen.
    widget_on_screen_type: ClassVar[type]
    enter_animation: TimedAnimationSpec | None = None
    exit_animation: TimedAnimationSpec | None = default(
        lambda self: self._init_exit_animation
    )

    def widget_on_screen(
        self,
        name_to_on_screens: dict[str, Coordinate | AreaOnScreen],
        parent: Scene | None,
    ) -> WidgetOnScreen:
        return self.widget_on_screen_type(
            widget=self, name_to_on_screens=name_to_on_screens, parent=parent
        )

    @property
    def _init_exit_animation(self) -> TimedAnimationOnScreens | None:
        if self.enter_animation:
            return self.enter_animation.reverse
        return None
