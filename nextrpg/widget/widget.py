from abc import abstractmethod
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import ClassVar, Self, override

from frozendict import frozendict

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.animation.timed_animation_spec import TimedAnimationSpec
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.metadata import HasMetadata, Metadata
from nextrpg.core.time import Millisecond
from nextrpg.core.util import type_name
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, is_key_press
from nextrpg.game.game_state import GameState
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.scene.scene import Scene


@dataclass_with_default(frozen=True)
class WidgetOnScreen(Scene):
    widget: Widget
    name_to_on_screens: frozendict[str, Coordinate | AreaOnScreen]
    parent: Scene | None = field(default=None, repr=False)
    is_selected: bool = False
    _: KW_ONLY = private_init_below()
    _enter_animation: TimedAnimationOnScreens | None = default(
        lambda self: self._init_enter_animation
    )
    _exit_animation: TimedAnimationOnScreens | None = None
    _tick_parent: bool = True
    _to_scene: Scene | None = None

    @cached_property
    def on_screen(self) -> Coordinate | AreaOnScreen | None:
        assert (
            self.widget.name
        ), f"Require widget.name to get on_screen. Got {self.widget}"
        return self.name_to_on_screens.get(self.widget.name)

    @cached_property
    def root(self) -> Scene:
        if isinstance(self.parent, WidgetOnScreen):
            return self.parent.root
        if self.parent:
            return self.parent
        return self

    @override
    def __str__(self) -> str:
        return f"{type_name(self)}({self.widget})"

    @cached_property
    def select(self) -> Self:
        return replace(self, is_selected=True)

    @cached_property
    def deselect(self) -> Self:
        return replace(self, is_selected=False)

    @override
    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Scene, GameState]:
        if self._tick_parent and self.parent:
            parent, state = self.parent.tick(time_delta, state)
        else:
            parent = self.parent
        if res := self._tick_without_parent(time_delta, state):
            ticked, state = res
            ticked = replace(ticked, parent=parent)
            return ticked, state
        return parent, state

    def _tick_without_parent(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState] | None:
        # Entering.
        if self._enter_animation:
            if (
                enter_animation := self._enter_animation.tick(time_delta)
            ) and enter_animation.is_complete:
                enter_animation = None
            ticked = replace(self, _enter_animation=enter_animation)
            return ticked, state

        # In widget.
        if not self._exit_animation:
            return self._tick_without_parent_and_animation(time_delta, state)

        # Exiting.
        if (
            exit_animation := self._exit_animation.tick(time_delta)
        ) and exit_animation.is_complete:
            return None
        ticked = replace(self, _exit_animation=exit_animation)
        return ticked, state

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
    def event(
        self, event: IoEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        # Entering.
        if self._enter_animation:
            return self, state

        # In widget.
        if not self._exit_animation:
            if not self.is_selected:
                return self, state
            if is_key_press(event, KeyMappingConfig.cancel) and self.parent:
                exit_scene = self.exit(self.parent)
                return exit_scene, state
            return self._event_after_selected(event, state)

        # Exiting.
        return self, state

    def with_parent(self, parent: Scene | None) -> Self:
        return replace(self, parent=parent)

    def exit(self, scene: Scene) -> Scene:
        if exit_animation := self._init_exit_animation:
            return replace(
                self, _exit_animation=exit_animation, _to_scene=scene
            )
        return scene

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
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        return self, state

    @property
    @abstractmethod
    def _drawing_on_screens_without_parent_and_animation(
        self,
    ) -> tuple[DrawingOnScreen, ...]: ...

    def _event_after_selected(
        self, event: IoEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        return self, state

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


@dataclass_with_default(frozen=True)
class Widget[_WidgetOnScreen: WidgetOnScreen](HasMetadata):
    # Must be a subclass of WidgetOnScreen.
    widget_on_screen_type: ClassVar[type]
    enter_animation: TimedAnimationSpec | None = None
    exit_animation: TimedAnimationSpec | None = default(
        lambda self: self._init_exit_animation
    )
    name: str | None = None
    metadata: Metadata = ()

    def with_parent(self, parent: WidgetOnScreen) -> _WidgetOnScreen:
        return self.widget_on_screen_type(
            widget=self,
            name_to_on_screens=parent.name_to_on_screens,
            parent=parent,
        )

    @property
    def _init_exit_animation(self) -> TimedAnimationOnScreens | None:
        if self.enter_animation:
            return self.enter_animation.reverse
        return None
