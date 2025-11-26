from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import ClassVar, Literal, Self, override

from nextrpg.config.config import config
from nextrpg.config.widget.panel_config import PanelConfig
from nextrpg.core.dataclass_with_default import default, private_init_below
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.game.game_state import GameState
from nextrpg.geometry.anchor import Anchor
from nextrpg.geometry.area_on_screen import AreaOnScreen
from nextrpg.widget.scroll_direction import ScrollDirection
from nextrpg.widget.sizable_widget import SizableWidget, SizableWidgetOnScreen
from nextrpg.widget.widget_group import WidgetGroup, WidgetGroupOnScreen


@dataclass(frozen=True, kw_only=True)
class PanelOnScreen(WidgetGroupOnScreen):
    widget: Panel
    _: KW_ONLY = private_init_below()
    _visible: tuple[_IndexedChild, ...] = default(
        lambda self: (
            self._visible_children(self._children[0], Anchor.TOP_LEFT)
            if self._children
            else ()
        )
    )

    @cached_property
    def children_drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens = [
            drawing_on_screen
            for child in self._visible
            for drawing_on_screen in child.drawing_on_screens(
                self._selected_index
            )
        ]
        if self._visible[0].index != 0:
            if self._is_vertical:
                icon = self.widget.config.more_above_icon.drawing_on_screens(
                    self.area.top_center, Anchor.BOTTOM_CENTER
                )
            else:
                icon = self.widget.config.more_on_left_icon.drawing_on_screens(
                    self.area.center_left, Anchor.CENTER_RIGHT
                )
            drawing_on_screens += icon
        if self._visible[-1].index != self._last_index:
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

    @override
    def _tick_without_parent_and_animation(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        ticked, state = super()._tick_without_parent_and_animation(
            time_delta, state
        )
        visible: list[_IndexedChild] = []
        for child in self._visible:
            child, state = child.tick_without_parent(time_delta, state)
            visible.append(child)
        with_visible = replace(ticked, _visible=tuple(visible))
        return with_visible, state

    @cached_property
    def area(self) -> AreaOnScreen:
        assert isinstance(
            self.on_screen, AreaOnScreen
        ), f"Expect AreaOnScreen for {self.widget.name}. Got {self.on_screen}."
        return self.on_screen

    @override
    def _step(self, forward: bool) -> Self:
        stepped = super()._step(forward)
        if stepped._selected.deselect in self._visible:
            return stepped
        if forward:
            anchor = Anchor.TOP_LEFT
        else:
            anchor = Anchor.BOTTOM_RIGHT
        visible = stepped._visible_children(stepped._selected, anchor)
        return replace(stepped, _visible=visible)

    @cached_property
    def _is_vertical(self) -> bool:
        return self.widget.scroll_direction is ScrollDirection.VERTICAL

    @cached_property
    def _last_index(self) -> int:
        return len(self._children) - 1

    @cached_property
    def _selected_index(self) -> int:
        return self._children.index(self._selected)

    def _visible_children(
        self,
        sentinel: SizableWidgetOnScreen,
        anchor: Literal[Anchor.TOP_LEFT, Anchor.BOTTOM_RIGHT],
    ) -> tuple[_IndexedChild, ...]:
        res: list[_IndexedChild] = []
        if is_forward := anchor is Anchor.TOP_LEFT:
            iterable = enumerate(self._children)
            sign = 1
            padding = self.widget.config.padding.top_left
        else:
            iterable = reversed(list(enumerate(self._children)))
            sign = -1
            padding = self.widget.config.padding.bottom_right
        coordinate = self.area.at_anchor(anchor) + sign * padding

        found_sentinel = False
        for i, child in iterable:
            if not found_sentinel and child is not sentinel:
                continue
            anchored = child.anchored(coordinate, anchor)
            if i == self._selected_index:
                anchored = anchored.select
            anchored_drawing = DrawingOnScreens(
                anchored._drawing_on_screens_without_parent
            )
            if child is sentinel:
                found_sentinel = True
            elif anchored_drawing not in self.area:
                break
            indexed_child = _IndexedChild(i, anchored)
            res.append(indexed_child)
            if self._is_vertical:
                coordinate += sign * (
                    anchored_drawing.height + self.widget.config.padding.height
                )
            else:
                coordinate += sign * (
                    anchored_drawing.width + self.widget.config.padding.width
                )
        if is_forward:
            return tuple(res)
        else:
            return tuple(reversed(res))


@dataclass(frozen=True, kw_only=True)
class Panel(WidgetGroup[PanelOnScreen]):
    name: str
    children: tuple[SizableWidget, ...]
    config: PanelConfig = field(default_factory=lambda: config().widget.panel)
    _: KW_ONLY = private_init_below()
    widget_on_screen_type: ClassVar[type] = PanelOnScreen


@dataclass(frozen=True)
class _IndexedChild:
    index: int
    child: SizableWidgetOnScreen

    def tick_without_parent(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        if res := self.child._tick_without_parent(time_delta, state):
            child, state = res
            ticked = replace(self, child=child)
        else:
            ticked = self
        return ticked, state

    def drawing_on_screens(
        self, selected_index: int
    ) -> tuple[DrawingOnScreen, ...]:
        if self.index == selected_index:
            widget = self.child.select
        else:
            widget = self.child
        return widget._drawing_on_screens_without_parent
