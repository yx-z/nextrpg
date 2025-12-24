from abc import abstractmethod
from dataclasses import KW_ONLY, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from frozendict import frozendict

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.config.config import config
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.metadata import Metadata
from nextrpg.core.time import Millisecond
from nextrpg.core.util import type_name
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.text import Text
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.io_event import is_key_press
from nextrpg.game.game_state import GameState
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.coordinate import Coordinate
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.scene.scene import Scene
from nextrpg.widget.widget_interaction_result import (
    AddChildWidget,
    BaseWidgetInteractionResult,
    ReplaceByWidget,
)

if TYPE_CHECKING:
    from nextrpg.widget.widget_spec import WidgetSpec


@dataclass_with_default(frozen=True)
class Widget(Scene):
    spec: WidgetSpec
    name_to_on_screens: frozendict[str, Coordinate | AreaOnScreen]
    parent: Scene | None = field(default=None, repr=False)
    is_selected: bool = False
    _: KW_ONLY = private_init_below()
    _enter_animation: AnimationOnScreens | None = default(
        lambda self: self._init_enter_animation
    )
    _exit_animation: AnimationOnScreens | None = None
    _tick_parent: bool = True
    _exit_to: Scene | None = None

    @cached_property
    def on_screen(self) -> Coordinate | AreaOnScreen | None:
        assert (
            self.spec.name
        ), f"Require widget.name to get on_screen. Got {self.spec}"
        return self.name_to_on_screens.get(self.spec.name)

    @cached_property
    def root(self) -> Scene:
        if isinstance(self.parent, Widget):
            return self.parent.root
        if self.parent:
            return self.parent
        return self

    @override
    def __str__(self) -> str:
        return f"{type_name(self)}({self.spec})"

    def set_selected(self, is_selected: bool) -> Self:
        is_selected = self.spec.selectable and is_selected
        return replace(self, is_selected=is_selected)

    @cached_property
    def select(self) -> Self:
        return replace(self, is_selected=self.spec.selectable)

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

        assert (
            self._exit_to
        ), f"Exiting widget must have an exit_to. Got {self._exit_to}"
        return self._exit_to, state

    @cached_property
    def drawing_on_screens(self) -> DrawingOnScreens:
        if self.parent:
            parent_drawing_on_screens = self.parent.drawing_on_screens
        else:
            parent_drawing_on_screens = DrawingOnScreens()
        return (
            parent_drawing_on_screens
            + self._drawing_on_screens_without_parent
            + self._metadata_drawing_on_screens
            + self._link_to_parent
        )

    def match_metadata(self, other: Widget | WidgetSpec | Metadata) -> bool:
        return self.spec.match_metadata(other)

    @override
    def event(
        self, event: BaseEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        if isinstance(event, BaseWidgetInteractionResult):
            res = self._on_interact(event)
            return res, state

        # Entering.
        if self._enter_animation:
            return self, state

        # In widget.
        if not self._exit_animation:
            if not self.is_selected:
                return self, state
            if is_key_press(event, KeyMappingConfig.cancel) and self.parent:
                exit_scene = self.exit_to(self.parent)
                return exit_scene, state
            return self._event_after_selected(event, state)

        # Exiting.
        return self, state

    def with_parent(self, parent: Scene | None) -> Self:
        return replace(self, parent=parent)

    def exit_to(self, scene: Scene) -> Scene:
        if exit_animation := self._init_exit_animation:
            return replace(self, _exit_animation=exit_animation, _exit_to=scene)
        return scene

    def _on_interact(self, event: BaseWidgetInteractionResult) -> Widget:
        if not self.match_metadata(event.target):
            if isinstance(self.parent, Widget):
                parent = self.parent._on_interact(event)
            else:
                parent = self.parent
            return replace(self, parent=parent)

        match event:
            case AddChildWidget():
                return event.widget_spec.with_parent(self).set_selected(
                    self.is_selected
                )
            case ReplaceByWidget():
                return event.widget_spec.with_parent(self.parent).set_selected(
                    self.is_selected
                )
        return self

    @cached_property
    def _link_to_parent(self) -> DrawingOnScreens:
        from nextrpg.widget.widget_group import WidgetGroup

        if (
            not (debug := config().debug)
            or not (color := debug.widget_link_color)
            or not isinstance(self.parent, Widget)
        ):
            return DrawingOnScreens()

        if isinstance(self.parent, WidgetGroup):
            parent_coordinate = self.parent.group_drawing_on_screens.top_left
        else:
            parent_coordinate = (
                self.parent._drawing_on_screens_without_parent.top_left
            )
        self_coordinate = self._drawing_on_screens_without_parent.top_left
        link = PolylineOnScreen((parent_coordinate, self_coordinate))
        return link.fill(
            color, allow_background_in_debug=False
        ).drawing_on_screens

    @cached_property
    def _metadata_drawing_on_screens(self) -> DrawingOnScreens:
        if (
            not (debug := config().debug)
            or not debug.widget_metadata_text
            or not self.spec.metadata
        ):
            return DrawingOnScreens()

        metadata_text = ",".join(f"{k}={v}" for k, v in self.spec.metadata)
        return Text(metadata_text).drawing_on_screens(
            self._drawing_on_screens_without_parent.top_left
        )

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
        if not (
            exit_animation := self._exit_animation.tick(time_delta)
        ).is_complete:
            ticked = replace(self, _exit_animation=exit_animation)
            return ticked, state

        # Exited.
        return None

    @cached_property
    def _drawing_on_screens_without_parent(
        self,
    ) -> DrawingOnScreens:
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
    ) -> DrawingOnScreens: ...

    def _event_after_selected(
        self, event: BaseEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        return self, state

    @property
    def _init_enter_animation(self) -> AnimationOnScreens | None:
        if self.spec.enter_animation:
            return self.spec.enter_animation.animate_on_screen(
                self._drawing_on_screens_without_parent_and_animation
            )
        return None

    @property
    def _init_exit_animation(self) -> AnimationOnScreens | None:
        if self.spec.exit_animation:
            return self.spec.exit_animation.animate_on_screen(
                self._drawing_on_screens_without_parent_and_animation
            )
        return None
