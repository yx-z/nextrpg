from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from functools import cached_property
from itertools import cycle, pairwise
from typing import ClassVar, Self, override

from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.log import Log
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.scene.scene import Scene
from nextrpg.scene.ui.scroll_direction import ScrollDirection
from nextrpg.scene.ui.widget import Widget, WidgetOnScreen

log = Log()


@dataclass_with_default(frozen=True, kw_only=True)
class WidgetGroupOnScreen(WidgetOnScreen):
    widget_input: WidgetGroup
    _ = private_init_below()
    _children: tuple[WidgetOnScreen, ...] = default(
        lambda self: self._init_children
    )

    @override
    def event_after_selected(self, event: IoEvent) -> Scene:
        children: list[WidgetOnScreen] = []
        for child in self._children:
            if (
                child.is_selected
                and (res := child.event_after_selected(event)) is not child
            ):
                return res
            children.append(child)

        if isinstance(event, KeyPressDown):
            key = (self.widget_input.scroll_direction, event.key)
            forward = _SCROLL_AND_KEY_TO_FORWARD.get(key)
            if forward is not None:
                return self._step(forward)
        return self._with_children(children)

    @override
    @cached_property
    def drawing_on_screens_after_parent(self) -> tuple[DrawingOnScreen, ...]:
        return tuple(
            drawing_on_screen
            for child in self._children
            for drawing_on_screen in child.drawing_on_screens_after_parent
        )

    @override
    def tick_after_parent(self, time_delta: Millisecond) -> Self:
        children = tuple(
            child.tick_after_parent(time_delta) for child in self._children
        )
        return self._with_children(children)

    @cached_property
    def _selected(self) -> WidgetOnScreen | None:
        for child in self._children:
            if isinstance(child, WidgetOnScreen) and child.is_selected:
                return child
        return None

    @property
    def _init_children(self) -> tuple[WidgetOnScreen, ...]:
        assert (
            children := self.widget_input.children
        ), "Require non-empty children."
        return (self._init_child(children[0]).select,) + tuple(
            self._init_child(child) for child in children[1:]
        )

    def _init_child(self, child: Widget) -> WidgetOnScreen:
        return child.widget_on_screen(self.name_to_on_screens, self)

    def _step(self, forward: bool) -> Self:
        if len(self._children) < 2 or (
            not self.widget_input.loop
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
        log.debug(t"Move from {self._selected} to {target}")

        children: list[WidgetOnScreen] = []
        for child in self._children:
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
class WidgetGroup(Widget[WidgetGroupOnScreen]):
    children: tuple[Widget, ...]
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True
    widget_on_screen_type: ClassVar[type[WidgetGroupOnScreen]] = (
        WidgetGroupOnScreen
    )

    def __str__(self) -> str:
        children = ",".join(map(str, self.children))
        return f"WidgetGroup({children})"


_SCROLL_AND_KEY_TO_FORWARD: dict[tuple[ScrollDirection, KeyboardKey], bool] = {
    (ScrollDirection.HORIZONTAL, KeyboardKey.LEFT): False,
    (ScrollDirection.HORIZONTAL, KeyboardKey.RIGHT): True,
    (ScrollDirection.VERTICAL, KeyboardKey.UP): False,
    (ScrollDirection.VERTICAL, KeyboardKey.DOWN): True,
}
