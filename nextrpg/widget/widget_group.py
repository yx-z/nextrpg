from collections.abc import Iterable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from itertools import cycle, pairwise
from typing import ClassVar, Self, override

from nextrpg.animation.animation_on_screens import AnimationOnScreens
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.animation_on_screen_like import AnimationOnScreenLike
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.scene.scene import Scene
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.widget import Widget, WidgetOnScreen


@dataclass_with_default(frozen=True, kw_only=True)
class WidgetGroupOnScreen(WidgetOnScreen):
    widget: WidgetGroup
    background: AnimationOnScreenLike | tuple[AnimationOnScreenLike, ...] = ()
    _: KW_ONLY = private_init_below()
    _children: tuple[WidgetOnScreen, ...] = default(
        lambda self: self._init_children(self.widget.children)
    )
    _background: AnimationOnScreens = default(
        lambda self: self._init_background
    )

    @cached_property
    def children_drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return tuple(
            drawing_on_screen
            for child in self._children
            for drawing_on_screen in child._drawing_on_screens_after_parent
        )

    @property
    def _init_background(self) -> AnimationOnScreens:
        return AnimationOnScreens(self.background)

    @override
    def _event_after_selected(self, event: IoEvent) -> Scene:
        children: list[WidgetOnScreen] = []
        for child in self._children:
            if (
                child._is_selected
                and (res := child._event_after_selected(event)) is not child
            ):
                return res
            children.append(child)

        if isinstance(event, KeyPressDown):
            key = (self.widget.scroll_direction, event.key)
            forward = _SCROLL_AND_KEY_TO_FORWARD.get(key)
            if forward is not None:
                return self._step(forward)
        return self._with_children(children)

    @override
    @cached_property
    def _drawing_on_screens_after_parent(self) -> tuple[DrawingOnScreen, ...]:
        return (
            self._background.drawing_on_screens
            + self.children_drawing_on_screens
        )

    @override
    def _tick_after_parent(self, time_delta: Millisecond) -> Self:
        children = tuple(
            child._tick_after_parent(time_delta) for child in self._children
        )
        ticked = self._with_children(children)
        background = self._background.tick(time_delta)
        return replace(ticked, _background=background)

    @cached_property
    def _selected(self) -> WidgetOnScreen | None:
        for child in self._children:
            if isinstance(child, WidgetOnScreen) and child._is_selected:
                return child
        return None

    def _init_children(
        self, children: tuple[Widget, ...]
    ) -> tuple[WidgetOnScreen, ...]:
        assert children, "Require non-empty children."
        first_child_selected = self._init_child(children[0]).select
        remaining_deselected = tuple(
            self._init_child(child) for child in children[1:]
        )
        return (first_child_selected,) + remaining_deselected

    def _init_child(self, child: Widget) -> WidgetOnScreen:
        return child.widget_on_screen(self.name_to_on_screens, self)

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

    def _with_children(self, children: Iterable[WidgetOnScreen]) -> Self:
        children_with_parent = tuple(
            child.with_parent(self) for child in children
        )
        return replace(self, _children=children_with_parent)


@dataclass(frozen=True, kw_only=True)
class WidgetGroup(Widget):
    children: tuple[Widget, ...]
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = WidgetGroupOnScreen


_SCROLL_AND_KEY_TO_FORWARD: dict[tuple[ScrollDirection, KeyboardKey], bool] = {
    (ScrollDirection.HORIZONTAL, KeyboardKey.LEFT): False,
    (ScrollDirection.HORIZONTAL, KeyboardKey.RIGHT): True,
    (ScrollDirection.VERTICAL, KeyboardKey.UP): False,
    (ScrollDirection.VERTICAL, KeyboardKey.DOWN): True,
}
