from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from itertools import cycle, pairwise
from typing import ClassVar, Self, override

from nextrpg import private_init_below
from nextrpg.core.dataclass_with_default import dataclass_with_default, default
from nextrpg.core.time import Millisecond
from nextrpg.draw.drawing_on_screen import DrawingOnScreen
from nextrpg.event.io_event import IoEvent, KeyboardKey, KeyPressDown
from nextrpg.scene.scene import Scene
from nextrpg.ui.scroll_direction import ScrollDirection
from nextrpg.ui.selectable_widget import (
    SelectableWidget,
    SelectableWidgetOnScreen,
)
from nextrpg.ui.widget import Widget, WidgetOnScreen


@dataclass_with_default(frozen=True, kw_only=True)
class WidgetGroupOnScreen(SelectableWidgetOnScreen):
    widget_input: WidgetGroup
    _: KW_ONLY = private_init_below()
    _children: tuple[WidgetOnScreen, ...] = default(
        lambda self: tuple(
            widget.widget_on_screen(self.name_to_on_screens)
            for widget in self.widget_input.children
        )
    )

    @override
    def selected_event(
        self, event: IoEvent
    ) -> SelectableWidgetOnScreen | Scene:
        # Action on children first.
        children: list[WidgetOnScreen] = []
        widget_changed = False
        for child in self._children:
            if (
                not isinstance(child, SelectableWidgetOnScreen)
                or (res := child.event(event)) is child
            ):
                # No change on the widget.
                children.append(child)
                continue
            if isinstance(res, Scene):
                # New scene.
                return res

            widget_changed = True
            if res is None:
                # Dismiss widget.
                continue
            # Deselect the current widget. And select the new widget.
            children += [child.deselect, res.set_parent(child).select]
        if widget_changed:
            return replace(self, _children=tuple(children))

        if isinstance(event, KeyPressDown):
            match self.widget_input.scroll_direction:
                case ScrollDirection.HORIZONTAL:
                    match event.key:
                        case KeyboardKey.LEFT:
                            children = self._step(children, forward=False)
                        case KeyboardKey.RIGHT:
                            children = self._step(children, forward=True)
                case ScrollDirection.VERTICAL:
                    match event.key:
                        case KeyboardKey.UP:
                            children = self._step(children, forward=False)
                        case KeyboardKey.DOWN:
                            children = self._step(children, forward=True)
        return replace(self, _children=tuple(children))

    @override
    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return tuple(
            drawing_on_screen
            for child in self._children
            for drawing_on_screen in child.drawing_on_screens
        )

    @override
    def tick(self, time_delta: Millisecond) -> Self:
        children = tuple(widget.tick(time_delta) for widget in self._children)
        return replace(self, _children=children)

    @override
    @cached_property
    def select(self) -> Self:
        res: list[WidgetOnScreen] = []
        selected = False
        for child in self._children:
            if selected or not isinstance(child, SelectableWidgetOnScreen):
                res.append(child)
                continue
            res.append(child.select)
            selected = True
        return replace(super().select, _children=tuple(res))

    def _step(
        self, children: list[WidgetOnScreen], forward: bool
    ) -> list[WidgetOnScreen]:
        if len(selectable_widgets := self._selectable_widgets(children)) < 2:
            return children

        selected = self._selected(children)
        first = selectable_widgets[0]
        last = selectable_widgets[-1]
        if not self.widget_input.loop and (
            (not forward and selected is first)
            or (forward and selected is last)
        ):
            return children

        prev = None
        nxt = None
        for w1, w2 in pairwise(cycle(selectable_widgets)):
            if w1 is selected:
                prev, nxt = w1, w2
                break

        if forward:
            target = nxt
        else:
            target = prev
        assert target

        res: list[WidgetOnScreen] = []
        for child in children:
            if child is selected:
                assert isinstance(child, SelectableWidgetOnScreen)
                child = child.deselect
            if child is target:
                child = child.select
            res.append(child)
        return res

    def _selectable_widgets(
        self, children: list[WidgetOnScreen]
    ) -> tuple[SelectableWidgetOnScreen, ...]:
        return tuple(
            widget
            for widget in children
            if isinstance(widget, SelectableWidgetOnScreen)
        )

    def _selected(
        self, children: list[WidgetOnScreen]
    ) -> SelectableWidgetOnScreen:
        for child in children:
            if (
                isinstance(child, SelectableWidgetOnScreen)
                and child.is_selected
            ):
                return child
        raise RuntimeError(f"No selected widget in {self}")


@dataclass(frozen=True)
class WidgetGroup(SelectableWidget[WidgetGroupOnScreen]):
    children: tuple[Widget, ...]
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True
    widget_on_screen_type: ClassVar[type[WidgetGroupOnScreen]] = (
        WidgetGroupOnScreen
    )
