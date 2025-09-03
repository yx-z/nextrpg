from __future__ import annotations

from collections.abc import Iterable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from itertools import cycle, pairwise
from typing import ClassVar, Self, override

from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
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
            child.widget_on_screen(self.name_to_on_screens)
            for child in self.widget_input.children
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
            if res is not None:
                # Deselect the current widget. And select the new widget.
                children += [child.deselect, res.set_parent(child).select]
            # Dismiss the widget if res is None.

        if not widget_changed and isinstance(event, KeyPressDown):
            key = (self.widget_input.scroll_direction, event.key)
            forward = _SCROLL_AND_KEY_TO_FORWARD.get(key)
            if forward is not None:
                return self._step(forward)
        return self._with_children(children)

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
        children = tuple(child.tick(time_delta) for child in self._children)
        return self._with_children(children)

    @override
    @cached_property
    def select(self) -> Self:
        res: list[WidgetOnScreen] = []
        selected = False
        for child in self._children:
            if not selected and isinstance(child, SelectableWidgetOnScreen):
                res.append(child.select)
                selected = True
            else:
                res.append(child)
        return replace(super().select, _children=tuple(res))

    @cached_property
    def selected(self) -> SelectableWidgetOnScreen | None:
        for child in self._children:
            if (
                isinstance(child, SelectableWidgetOnScreen)
                and child.is_selected
            ):
                return child
        return None

    def _step(self, forward: bool) -> Self:
        if len(self._selectable_widgets) < 2 or (
            not self.widget_input.loop
            and (
                (not forward and self.selected is self._selectable_widgets[0])
                or (forward and self.selected is self._selectable_widgets[-1])
            )
        ):
            return self

        target: SelectableWidgetOnScreen | None = None
        for w1, w2 in pairwise(cycle(self._selectable_widgets)):
            if not forward and w2 is self.selected:
                target = w1
                break
            if forward and w1 is self.selected:
                target = w2
                break
        assert target

        children: list[WidgetOnScreen] = []
        for child in self._children:
            if child is self.selected:
                child = self.selected.deselect
            elif child is target:
                child = target.select
            children.append(child)
        return self._with_children(children)

    @cached_property
    def _selectable_widgets(self) -> tuple[SelectableWidgetOnScreen, ...]:
        return tuple(
            child
            for child in self._children
            if isinstance(child, SelectableWidgetOnScreen)
        )

    def _with_children(self, children: Iterable[WidgetOnScreen]) -> Self:
        return replace(self, _children=tuple(children))


@dataclass(frozen=True, kw_only=True)
class WidgetGroup(SelectableWidget[WidgetGroupOnScreen]):
    children: tuple[Widget, ...]
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL
    loop: bool = True
    widget_on_screen_type: ClassVar[type[WidgetGroupOnScreen]] = (
        WidgetGroupOnScreen
    )


_SCROLL_AND_KEY_TO_FORWARD: dict[tuple[ScrollDirection, KeyboardKey], bool] = {
    (ScrollDirection.HORIZONTAL, KeyboardKey.LEFT): False,
    (ScrollDirection.HORIZONTAL, KeyboardKey.RIGHT): True,
    (ScrollDirection.VERTICAL, KeyboardKey.UP): False,
    (ScrollDirection.VERTICAL, KeyboardKey.DOWN): True,
}
