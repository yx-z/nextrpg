from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from enum import Enum, auto
from functools import cached_property
from typing import ClassVar, Generic, Self, TypeVar, override

from nextrpg.animation.animation_on_screen import (
    AnimationOnScreen,
    tick_optional,
)
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
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


@dataclass_with_default(frozen=True)
class WidgetOnScreen(Scene):
    widget_input: Widget
    name_to_on_screens: dict[str, Coordinate | AreaOnScreen]
    parent: Scene | None = None
    _: KW_ONLY = private_init_below()
    _is_selected: bool = False
    _state: WidgetOnScreenState = WidgetOnScreenState.ON_SCREEN
    _to_scene: Scene | None = None
    _animation: AnimationOnScreen | None = default(
        lambda self: self._init_animation
    )

    def exit(self, to_scene: Scene) -> Self:
        if self.widget_input.exiting_animation:
            animation = self.widget_input.exiting_animation(
                self.drawing_on_screens_after_parent
            )
            return replace(self, _animation=animation, _to_scene=to_scene)
        return to_scene

    @property
    def select(self) -> Self:
        return replace(self, _is_selected=True)

    @property
    def deselect(self) -> Self:
        return replace(self, _is_selected=False)

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        if self._animation:
            if (animation := self._animation.tick(time_delta)).complete:
                if self._to_scene:
                    return self._to_scene
                animation = None
        else:
            animation = None

        parent = tick_optional(self.parent, time_delta)
        to_scene = tick_optional(self._to_scene, time_delta)
        ticked = self.tick_after_parent(time_delta)
        return replace(
            ticked, _animation=animation, parent=parent, _to_scene=to_scene
        )

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        if self.parent:
            parent = self.parent.drawing_on_screens
        else:
            parent = ()
        if self._animation:
            return parent + self._animation.drawing_on_screens
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
            return self.exit(self.parent)
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

    @property
    def _init_animation(self) -> AnimationOnScreen | None:
        if self.widget_input.entering_animation:
            return self.widget_input.entering_animation(
                self.drawing_on_screens_after_parent
            )
        return None


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
