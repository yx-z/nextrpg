from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import ClassVar, Iterable, Self, override

from nextrpg.config.config import config
from nextrpg.config.widget.panel_config import PanelConfig
from nextrpg.core.dataclass_with_default import default, private_init_below
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.geometry.size import ZERO_HEIGHT, ZERO_WIDTH
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.sizable_widget import SizableWidget, SizableWidgetOnScreen
from nextrpg.widget.widget import Widget, WidgetOnScreen
from nextrpg.widget.widget_group import WidgetGroup, WidgetGroupOnScreen


@dataclass(frozen=True, kw_only=True)
class PanelOnScreen(WidgetGroupOnScreen):
    widget: Panel
    _: KW_ONLY = private_init_below()
    _visible: range = default(lambda self: self._init_visible)

    @cached_property
    def children_drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens = [
            DrawingOnScreens(
                self._children[i]._drawing_on_screens_without_parent
            )
            for i in self._visible
        ]
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
    def _step(self, forward: bool) -> Self:
        stepped = super()._step(forward)

    @property
    def _init_visible(self) -> range:
        end = 1
        if self._is_vertical:
            height = ZERO_HEIGHT
            while end <= len(self._children) and height < self.area.height:
                height += self._children[end - 1].widget.size.height
                end += 1
        else:
            width = ZERO_WIDTH
            while end <= len(self._children) and width < self.area.width:
                width += self._children[end - 1].widget.size.width
        return range(end)

    @override
    def _init_children(
        self, children: Iterable[Widget]
    ) -> tuple[WidgetOnScreen, ...]:
        children_on_screen: tuple[SizableWidgetOnScreen, ...] = (
            super()._init_children(children)
        )
        top_left = self.area.points[0] + self.widget.config.padding.top_left
        res: list[WidgetOnScreen] = []
        for child in children_on_screen:
            anchored = child.widget.anchored(top_left)
            child_widget_on_screen = replace(child, widget=anchored)
            res.append(child_widget_on_screen)
            if self._is_vertical:
                top_left += (
                    anchored.size.height + self.widget.config.padding.height
                )
            else:
                top_left += (
                    anchored.size.width + self.widget.config.padding.width
                )
        return tuple(res)

    @cached_property
    def _is_vertical(self) -> bool:
        return self.widget.scroll_direction is ScrollDirection.VERTICAL


@dataclass(frozen=True, kw_only=True)
class Panel(WidgetGroup[PanelOnScreen]):
    name: str
    children: tuple[SizableWidget, ...]
    config: PanelConfig = field(default_factory=lambda: config().widget.panel)
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = PanelOnScreen
