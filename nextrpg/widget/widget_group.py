from collections.abc import Callable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from itertools import cycle, pairwise
from typing import ClassVar, Self, override

from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.sprite import tick_optional
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.event.io_event import IoEvent, KeyPressDown
from nextrpg.game.game_state import GameState
from nextrpg.scene.scene import Scene
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.widget import Widget, WidgetOnScreen


@dataclass_with_default(frozen=True, kw_only=True)
class WidgetGroupOnScreen(WidgetOnScreen):
    widget: WidgetGroup
    background: SpriteOnScreen | None = None
    _: KW_ONLY = private_init_below()
    _children: tuple[WidgetOnScreen, ...] = default(
        lambda self: self._init_children(self.widget.children)
    )

    @cached_property
    def children_drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return tuple(
            drawing_on_screen
            for child in self._children
            for drawing_on_screen in child._drawing_on_screens_without_parent
        )

    def replace(
        self, from_child: WidgetOnScreen, to_child: WidgetOnScreen
    ) -> Self:
        assert (
            meta := from_child.widget.metadata
        ), f"Require non-empty metadata matching to replace widget from {from_child}."
        children = tuple(
            to_child.select if child.widget.metadata == meta else child
            for child in self._children
        )
        return replace(self, _children=children)

    @override
    def _event_after_selected(
        self, event: IoEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        children: list[WidgetOnScreen] = []
        for child in self._children:
            if (
                child._is_selected
                and (res := child._event_after_selected(event, state))[0]
                is not child
            ):
                return res
            children.append(child)

        if isinstance(event, KeyPressDown):
            key = (self.widget.scroll_direction, event.key_mapping)
            if (forward := _SCROLL_AND_KEY_TO_FORWARD.get(key)) is not None:
                stepped = self._step(forward)
                return stepped, state
        with_children = self._with_children(children)
        return with_children, state

    @override
    @cached_property
    def _drawing_on_screens_without_parent_and_animation(
        self,
    ) -> tuple[DrawingOnScreen, ...]:
        if self.background:
            drawing_on_screens = self.background.drawing_on_screens
        else:
            drawing_on_screens = ()
        return drawing_on_screens + self.children_drawing_on_screens

    @override
    def _tick_without_parent_and_animation(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        children: list[WidgetOnScreen] = []
        for child in self._children:
            if res := child._tick_without_parent(time_delta, state):
                child, state = res
                children.append(child)
        ticked = self._with_children(children)
        background = tick_optional(self.background, time_delta)
        ticked_with_background = replace(ticked, background=background)
        return ticked_with_background, state

    @cached_property
    def _selected(self) -> WidgetOnScreen | None:
        for child in self._children:
            if isinstance(child, WidgetOnScreen) and child._is_selected:
                return child
        return None

    def _init_children(
        self,
        children: (
            tuple[Widget, ...]
            | Callable[[WidgetGroupOnScreen], tuple[Widget, ...]]
        ),
    ) -> tuple[WidgetOnScreen, ...]:
        if callable(children):
            children = children(self)
        assert children, "Require non-empty children."
        first_child_selected = children[0].with_parent(self).select
        remaining_deselected = tuple(
            child.with_parent(self) for child in children[1:]
        )
        return (first_child_selected,) + remaining_deselected

    def _step(self, forward: bool) -> Self:
        if len(self._children) < 2 or (
            not self.widget.loop
            and (
                (not forward and self._selected is self._children[0])
                or (forward and self._selected is self._children[-1])
            )
        ):
            return self

        for w1, w2 in pairwise(cycle(self._children)):
            if not forward and w2 is self._selected:
                target = w1
                break
            if forward and w1 is self._selected:
                target = w2
                break

        children: list[WidgetOnScreen] = []
        for i, child in enumerate(self._children):
            if child is self._selected:
                child = self._selected.deselect
            elif child is target:
                child = target.select
            children.append(child)
        return self._with_children(children)

    def _with_children(self, children: list[WidgetOnScreen]) -> Self:
        children_with_parent = tuple(
            child.with_parent(self) for child in children
        )
        return replace(self, _children=children_with_parent)


@dataclass(frozen=True, kw_only=True)
class WidgetGroup[_WidgetGroupOnScreen: WidgetOnScreen](
    Widget[_WidgetGroupOnScreen]
):
    children: (
        tuple[Widget, ...] | Callable[[WidgetGroupOnScreen], tuple[Widget, ...]]
    )
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = WidgetGroupOnScreen


_SCROLL_AND_KEY_TO_FORWARD = {
    (ScrollDirection.HORIZONTAL, KeyMappingConfig.left): False,
    (ScrollDirection.HORIZONTAL, KeyMappingConfig.right): True,
    (ScrollDirection.VERTICAL, KeyMappingConfig.up): False,
    (ScrollDirection.VERTICAL, KeyMappingConfig.down): True,
}
