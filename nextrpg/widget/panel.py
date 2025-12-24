from collections.abc import Iterable
from dataclasses import KW_ONLY, dataclass, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg.core.dataclass_with_default import default, private_init_below
from nextrpg.drawing.drawing_on_screens import (
    DrawingOnScreens,
    drawing_on_screens,
)
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.size import Height, Width
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.sizable_widget import SizableWidget
from nextrpg.widget.widget import Widget
from nextrpg.widget.widget_group import WidgetGroup
from nextrpg.widget.widget_interaction_result import BaseWidgetInteractionResult

if TYPE_CHECKING:
    from nextrpg.widget.panel_spec import PanelSpec


@dataclass(frozen=True, kw_only=True)
class Panel(WidgetGroup):
    spec: PanelSpec
    _: KW_ONLY = private_init_below()
    _visible: range = default(lambda self: self._visible_range_forward)

    @cached_property
    def area(self) -> AreaOnScreen:
        assert isinstance(
            self.on_screen, AreaOnScreen
        ), f"Expect AreaOnScreen for {self.spec.name}. Got {self.on_screen}."
        return self.on_screen

    @override
    def _on_interact(self, event: BaseWidgetInteractionResult) -> Widget:
        if isinstance(res := super()._on_interact(event), Panel):
            return replace(res, _visible=res._visible_range_forward)
        return res

    @cached_property
    def _group_drawing_on_screens(self) -> DrawingOnScreens:
        return (
            self._visible_drawing_on_screens
            + self._more_before_icon
            + self._more_after_icon
        )

    @cached_property
    def _more_after_icon(self) -> DrawingOnScreens:
        if self._visible.stop == len(self._group) or self.spec.loop:
            return DrawingOnScreens()
        if self._is_vertical:
            return self.spec.config.more_below_icon.drawing_on_screens(
                self.area.bottom_center, Anchor.TOP_CENTER
            )
        return self.spec.config.more_on_right_icon.drawing_on_screens(
            self.area.center_right, Anchor.CENTER_LEFT
        )

    @cached_property
    def _more_before_icon(self) -> DrawingOnScreens:
        if not self._visible.start or self.spec.loop:
            return DrawingOnScreens()
        if self._is_vertical:
            return self.spec.config.more_above_icon.drawing_on_screens(
                self.area.top_center, Anchor.BOTTOM_CENTER
            )
        return self.spec.config.more_on_left_icon.drawing_on_screens(
            self.area.center_left, Anchor.CENTER_RIGHT
        )

    @property
    def _visible_widgets(
        self,
    ) -> Iterable[_SizableWidgetAndDrawingOnScreens]:
        coordinate = self.area.at_anchor(self._anchor) + self._initial_padding
        for i in self._visible:
            anchored = self._group[i].anchored(coordinate, self._anchor)
            yield _SizableWidgetAndDrawingOnScreens(
                anchored,
                anchored._drawing_on_screens_without_parent,
            )
            coordinate += self._to_next_widget(
                anchored._drawing_on_screens_without_parent
            )

    @cached_property
    def _visible_drawing_on_screens(
        self,
    ) -> DrawingOnScreens:
        return drawing_on_screens(
            widget.drawing_on_screens for widget in self._visible_widgets
        )

    @override
    @cached_property
    def _metadata_drawing_on_screens(self) -> DrawingOnScreens:
        metadata = drawing_on_screens(
            widget.widget._metadata_drawing_on_screens
            for widget in self._visible_widgets
        )
        return Widget._metadata_drawing_on_screens.__get__(self) + metadata

    @override
    def _step(self, is_forward: bool) -> Self:
        stepped = super()._step(is_forward)
        if stepped._selected_index in stepped._visible:
            return stepped
        if is_forward:
            visible = stepped._visible_range_forward
        else:
            visible = stepped._visible_range_backward
        return replace(stepped, _visible=visible)

    @cached_property
    def _is_vertical(self) -> bool:
        return self.spec.scroll_direction is ScrollDirection.VERTICAL

    @cached_property
    def _selected_index(self) -> int:
        return self._group.index(self._selected)

    @cached_property
    def _visible_range_backward(self) -> range:
        spec = replace(self.spec, loop=True)
        allow_loop = replace(self, spec=spec)
        stepped = allow_loop._step(is_forward=True)
        while self._selected_index != stepped._selected_index:
            stepped = stepped._step(is_forward=True)
        return stepped._visible

    @cached_property
    def _visible_range_forward(self) -> range:
        if not self._group:
            return range(0)
        coordinate = self.area.at_anchor(self._anchor) + self._initial_padding
        found = False
        for i, widget in enumerate(self._group):
            if not found:
                if i == self._selected_index:
                    found = True
                else:
                    continue
            anchored = widget.anchored(coordinate, self._anchor)
            anchored_drawing_on_screens = DrawingOnScreens(
                anchored._drawing_on_screens_without_parent
            )
            if (
                anchored_drawing_on_screens.rectangle_area_on_screen
                not in self.area
            ):
                return range(self._selected_index, i)
            coordinate += self._to_next_widget(anchored_drawing_on_screens)
        return range(self._selected_index, len(self._group))

    def _to_next_widget(self, current: DrawingOnScreens) -> Width | Height:
        if self._is_vertical:
            return current.height + self.spec.config.padding.height
        return current.width + self.spec.config.padding.width

    @cached_property
    def _anchor(self) -> Anchor:
        if self._is_vertical:
            return Anchor.TOP_CENTER
        return Anchor.CENTER_LEFT

    @cached_property
    def _initial_padding(self) -> Width | Height:
        if self._is_vertical:
            return self.spec.config.padding.top
        return self.spec.config.padding.left


@dataclass(frozen=True)
class _SizableWidgetAndDrawingOnScreens:
    widget: SizableWidget
    drawing_on_screens: DrawingOnScreens
