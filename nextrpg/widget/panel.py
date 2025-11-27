from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import ClassVar, Self, override

from nextrpg import Coordinate
from nextrpg.config.config import config
from nextrpg.config.widget.panel_config import PanelConfig
from nextrpg.core.dataclass_with_default import default, private_init_below
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.size import Height, Width
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.sizable_widget import SizableWidget, SizableWidgetOnScreen
from nextrpg.widget.widget_group import WidgetGroup, WidgetGroupOnScreen


@dataclass(frozen=True, kw_only=True)
class PanelOnScreen(WidgetGroupOnScreen):
    widget: Panel
    _: KW_ONLY = private_init_below()
    _visible: range = default(lambda self: self._visible_range(is_forward=True))

    @cached_property
    def children_drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens: list[DrawingOnScreen] = []
        coordinate = self.area.at_anchor(self._anchor) + self._initial_padding
        for i in self._visible:
            child = self._children[i]
            anchored_drawing = self._child_drawing(child, coordinate)
            drawing_on_screens += anchored_drawing.drawing_on_screens
            coordinate += self._to_next_child(anchored_drawing)

        if self._visible.start != 0:
            if self._is_vertical:
                icon = self.widget.config.more_above_icon.drawing_on_screens(
                    self.area.top_center, Anchor.BOTTOM_CENTER
                )
            else:
                icon = self.widget.config.more_on_left_icon.drawing_on_screens(
                    self.area.center_left, Anchor.CENTER_RIGHT
                )
            drawing_on_screens += icon
        if self._visible.stop != len(self._children):
            if self._is_vertical:
                icon = self.widget.config.more_below_icon.drawing_on_screens(
                    self.area.bottom_center, Anchor.TOP_CENTER
                )
            else:
                icon = self.widget.config.more_on_right_icon.drawing_on_screens(
                    self.area.center_right, Anchor.CENTER_LEFT
                )
            drawing_on_screens += icon
        return tuple(drawing_on_screens)

    @cached_property
    def area(self) -> AreaOnScreen:
        assert isinstance(
            self.on_screen, AreaOnScreen
        ), f"Expect AreaOnScreen for {self.widget.name}. Got {self.on_screen}."
        return self.on_screen

    @override
    def _step(self, is_forward: bool) -> Self:
        stepped = super()._step(is_forward)
        if stepped._selected_index in stepped._visible:
            return stepped
        visible = stepped._visible_range(is_forward)
        return replace(stepped, _visible=visible)

    @cached_property
    def _is_vertical(self) -> bool:
        return self.widget.scroll_direction is ScrollDirection.VERTICAL

    @cached_property
    def _selected_index(self) -> int:
        return self._children.index(self._selected)

    def _visible_range(self, is_forward: bool) -> range:
        if not self._children:
            return range(0)

        if not is_forward:
            widget = replace(self.widget, loop=True)
            allow_loop = replace(self, widget=widget)
            stepped = allow_loop._step(is_forward=True)
            while self._selected_index != stepped._selected_index:
                stepped = stepped._step(is_forward=True)
            return stepped._visible

        coordinate = self.area.at_anchor(self._anchor) + self._initial_padding
        found = False
        for i, child in enumerate(self._children):
            if not found:
                if i == self._selected_index:
                    found = True
                else:
                    continue
            anchored_drawing = self._child_drawing(child, coordinate)
            if (
                i != self._selected_index
                and anchored_drawing.rectangle_area_on_screen not in self.area
            ):
                break
            coordinate += self._to_next_child(anchored_drawing)
        else:
            return range(self._selected_index, len(self._children))
        return range(self._selected_index, i)

    def _to_next_child(self, current_child: DrawingOnScreens) -> Width | Height:
        if self._is_vertical:
            return current_child.height + self.widget.config.padding.height
        return current_child.width + self.widget.config.padding.width

    def _child_drawing(
        self, child: SizableWidgetOnScreen, coordinate: Coordinate
    ) -> DrawingOnScreens:
        anchored = child.anchored(coordinate, self._anchor)
        return DrawingOnScreens(anchored._drawing_on_screens_without_parent)

    @cached_property
    def _anchor(self) -> Anchor:
        if self._is_vertical:
            return Anchor.TOP_CENTER
        return Anchor.CENTER_LEFT

    @cached_property
    def _initial_padding(self) -> Width | Height:
        if self._is_vertical:
            return self.widget.config.padding.top
        return self.widget.config.padding.left


@dataclass(frozen=True, kw_only=True)
class Panel(WidgetGroup[PanelOnScreen]):
    name: str
    children: tuple[SizableWidget, ...]
    config: PanelConfig = field(default_factory=lambda: config().widget.panel)
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = PanelOnScreen
