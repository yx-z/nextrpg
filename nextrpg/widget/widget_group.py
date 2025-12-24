from collections.abc import Collection, Iterable
from dataclasses import KW_ONLY, replace
from functools import cached_property
from itertools import cycle, pairwise
from typing import TYPE_CHECKING, Self, override

from nextrpg.config.config import config
from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
    default,
    private_init_below,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screens import (
    DrawingOnScreens,
    drawing_on_screens,
)
from nextrpg.drawing.sprite import tick_optional
from nextrpg.drawing.sprite_on_screen import (
    SpriteOnScreen,
)
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.io_event import KeyPressDown
from nextrpg.game.game_state import GameState
from nextrpg.geometry.polyline_on_screen import PolylineOnScreen
from nextrpg.scene.scene import Scene
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.widget import Widget
from nextrpg.widget.widget_interaction_result import (
    BaseWidgetInteractionResult,
    ReplaceByWidget,
)

if TYPE_CHECKING:
    from nextrpg.widget.widget_group_spec import WidgetGroupSpec
    from nextrpg.widget.widget_spec import WidgetSpec


@dataclass_with_default(frozen=True, kw_only=True)
class WidgetGroup(Widget):
    spec: WidgetGroupSpec
    background: SpriteOnScreen | None = None
    _: KW_ONLY = private_init_below()
    _group: tuple[Widget, ...] = default(
        lambda self: self._init_group(self.spec.widgets)
    )

    @cached_property
    def group_drawing_on_screens(self) -> DrawingOnScreens:
        return self._group_drawing_on_screens + self._widget_group_border

    @override
    def _on_interact(self, event: BaseWidgetInteractionResult) -> Widget:
        if isinstance(event, ReplaceByWidget):
            group = [
                (
                    widget._on_interact(event)
                    if widget.match_metadata(event.target)
                    else widget
                )
                for widget in self._group
            ]
            res = self._with_group(group)
        else:
            res = self
        return Widget._on_interact(res, event)

    @cached_property
    def _widget_group_border(self) -> DrawingOnScreens:
        if not (debug := config().debug) or not (
            color := debug.widget_group_border
        ):
            return DrawingOnScreens()
        line = PolylineOnScreen(
            self._group_drawing_on_screens.rectangle_area_on_screen.points
        )
        return line.fill(
            color, closed=True, allow_background_in_debug=False
        ).drawing_on_screens

    @cached_property
    def _group_drawing_on_screens(self) -> DrawingOnScreens:
        return drawing_on_screens(
            widget._drawing_on_screens_without_parent for widget in self._group
        )

    @override
    @cached_property
    def _metadata_drawing_on_screens(self) -> DrawingOnScreens:
        widget_metadata_drawing_on_screens = drawing_on_screens(
            widget._metadata_drawing_on_screens for widget in self._group
        )
        return (
            super()._metadata_drawing_on_screens
            + widget_metadata_drawing_on_screens
        )

    def _init_group(
        self, widgets: WidgetSpec | Collection[WidgetSpec]
    ) -> tuple[Widget, ...]:
        from nextrpg.widget.widget_spec import WidgetSpec

        if not widgets:
            return ()
        if isinstance(widgets, WidgetSpec):
            with_parent = (widgets.with_parent(self),)
        else:
            with_parent = tuple(w.with_parent(self) for w in widgets)
        if any(widget.is_selected for widget in with_parent):
            return with_parent
        return (with_parent[0].select,) + with_parent[1:]

    @override
    def _event_after_selected(
        self, event: BaseEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        group: list[Widget] = []
        for widget in self._group:
            if widget.is_selected and (
                res := widget._event_after_selected(event, state)
            ) != (widget, state):
                return res
            group.append(widget)

        if isinstance(event, KeyPressDown):
            key = (self.spec.scroll_direction, event.key_mapping)
            if (
                is_forward := _SCROLL_AND_KEY_TO_IS_FORWARD.get(key)
            ) is not None:
                stepped = self._step(is_forward)
                return stepped, state
        with_group = self._with_group(group)
        return with_group, state

    @cached_property
    def _selected(self) -> Widget | None:
        for widget in self._selectable_widgets:
            if widget.is_selected:
                return widget
        return None

    @override
    @cached_property
    def _drawing_on_screens_without_parent_and_animation(
        self,
    ) -> DrawingOnScreens:
        if self.background:
            background = self.background.drawing_on_screens
        else:
            background = DrawingOnScreens()
        return background + self.group_drawing_on_screens

    @override
    def _tick_without_parent_and_animation(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        group: list[Widget] = []
        for widget in self._group:
            if res := widget._tick_without_parent(time_delta, state):
                widget, state = res
                group.append(widget)
        ticked = self._with_group(group)
        background = tick_optional(self.background, time_delta)
        ticked_with_background = replace(ticked, background=background)
        return ticked_with_background, state

    @cached_property
    def _selectable_widgets(self) -> tuple[Widget, ...]:
        return tuple(c for c in self._group if c.spec.selectable)

    def _step(self, is_forward: bool) -> Self:
        if len(self._selectable_widgets) < 2:
            return self
        if not self.spec.loop:
            at_first = self._selected is self._selectable_widgets[0]
            at_last = self._selected is self._selectable_widgets[-1]
            if (is_forward and at_last) or (not is_forward and at_first):
                return self

        target: Widget | None = None
        for w1, w2 in pairwise(cycle(self._selectable_widgets)):
            if not is_forward and w2 is self._selected:
                target = w1
                break
            if is_forward and w1 is self._selected:
                target = w2
                break
        assert target, f"Expect not None target after selection in {self}"

        group: list[Widget] = []
        for i, widget in enumerate(self._group):
            if widget is self._selected:
                widget = self._selected.deselect
            elif widget is target:
                widget = target.select
            group.append(widget)
        return self._with_group(group)

    def _with_group(self, widgets: Iterable[Widget]) -> Self:
        widget_with_parent = tuple(
            widget.with_parent(self) for widget in widgets
        )
        return replace(self, _group=widget_with_parent)


_SCROLL_AND_KEY_TO_IS_FORWARD = {
    (ScrollDirection.HORIZONTAL, KeyMappingConfig.left): False,
    (ScrollDirection.HORIZONTAL, KeyMappingConfig.right): True,
    (ScrollDirection.VERTICAL, KeyMappingConfig.up): False,
    (ScrollDirection.VERTICAL, KeyMappingConfig.down): True,
}
