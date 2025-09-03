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
                            children = self._select_previous(children)
                        case KeyboardKey.RIGHT:
                            children = self._select_next(children)
                case ScrollDirection.VERTICAL:
                    match event.key:
                        case KeyboardKey.UP:
                            children = self._select_previous(children)
                        case KeyboardKey.DOWN:
                            children = self._select_next(children)
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

    def _select_previous(
        self, children: list[WidgetOnScreen]
    ) -> list[WidgetOnScreen]:
        if len(
            selectable_widgets := self._selectable_widgets(children)
        ) < 2 or (
            (selected := self._selected(children)) is selectable_widgets[0]
            and not self.widget_input.loop
        ):
            return children

        previous: SelectableWidgetOnScreen | None = None
        for previous, widget in pairwise(cycle(selectable_widgets)):
            if widget is selected:
                break
        assert previous

        res: list[WidgetOnScreen] = []
        for child in children:
            if child is selected:
                assert isinstance(child, SelectableWidgetOnScreen)
                child = child.deselect
            if child is previous:
                child = child.select
            res.append(child)
        return res

    def _select_next(
        self, children: list[WidgetOnScreen]
    ) -> list[WidgetOnScreen]:
        if len(
            selectable_widgets := self._selectable_widgets(children)
        ) < 2 or (
            (selected := self._selected(children)) is selectable_widgets[-1]
            and not self.widget_input.loop
        ):
            return children

        next_widget: SelectableWidgetOnScreen | None = None
        for widget, next_widget in pairwise(cycle(selectable_widgets)):
            if widget is selected:
                break
        assert next_widget

        res: list[WidgetOnScreen] = []
        for child in children:
            if child is selected:
                assert isinstance(child, SelectableWidgetOnScreen)
                child = child.deselect
            if child is next_widget:
                child = child.select
            res.append(child)
        return res

    def _selectable_widgets(
        self, children: list[WidgetOnScreen]
    ) -> list[SelectableWidgetOnScreen]:
        return [
            widget
            for widget in children
            if isinstance(widget, SelectableWidgetOnScreen)
        ]

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
