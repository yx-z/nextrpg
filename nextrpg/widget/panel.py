from dataclasses import KW_ONLY, dataclass, field, replace
from functools import cached_property
from typing import ClassVar, Self, override

from nextrpg.config.config import config
from nextrpg.config.widget.panel_config import PanelConfig
from nextrpg.core.dataclass_with_default import default, private_init_below
from nextrpg.core.time import Millisecond
from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
from nextrpg.drawing.drawing_on_screens import DrawingOnScreens
from nextrpg.drawing.sprite_on_screen import tick_all_with_state
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
        lambda self: self._visible_children(is_forward=True)
    )

    @cached_property
    def children_drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        drawing_on_screens = [
            drawing_on_screen
            for widget in self._visible
            for drawing_on_screen in widget.child._drawing_on_screens_without_parent
        ]
        if self._visible and self._visible[0].index != 0:
            if self._is_vertical:
                icon = self.widget.config.more_above_icon.drawing_on_screens(
                    self.area.top_center, Anchor.BOTTOM_CENTER
                )
            else:
                icon = self.widget.config.more_on_left_icon.drawing_on_screens(
                    self.area.center_left, Anchor.CENTER_RIGHT
                )
            drawing_on_screens += icon
        if self._visible and self._visible[-1].index != self._last_index:
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
        visible, state = tick_all_with_state(self._visible, time_delta, state)
        with_visible = replace(ticked, _visible=visible)
        return with_visible, state

    @cached_property
    def area(self) -> AreaOnScreen:
        assert isinstance(
            self.on_screen, AreaOnScreen
        ), f"Expect AreaOnScreen for {self.widget.name}. Got {self.on_screen}."
        return self.on_screen

    @override
    def _step(self, is_forward: bool) -> Self:
        stepped = super()._step(is_forward)
        if stepped._selected_index in stepped._visible_indices:
            visible = tuple(
                (
                    child.select
                    if child.index == stepped._selected_index
                    else child.deselect
                )
                for child in stepped._visible
            )
            return replace(stepped, _visible=visible)
        visible = stepped._visible_children(is_forward)
        return replace(stepped, _visible=visible)

    @cached_property
    def _visible_indices(self) -> tuple[int, ...]:
        return tuple(child.index for child in self._visible)

    @cached_property
    def _is_vertical(self) -> bool:
        return self.widget.scroll_direction is ScrollDirection.VERTICAL

    @cached_property
    def _last_index(self) -> int:
        return len(self._children) - 1

    @cached_property
    def _selected_index(self) -> int:
        return self._children.index(self._selected)

    def _visible_children(self, is_forward: bool) -> tuple[_IndexedChild, ...]:
        if not is_forward:
            stepped = self._step(is_forward=True)
            while self._selected_index != stepped._selected_index:
                stepped = stepped._step(is_forward=True)
            return stepped._visible

        res: list[_IndexedChild] = []
        if self._is_vertical:
            anchor = Anchor.TOP_CENTER
            padding = self.widget.config.padding.top
        else:
            anchor = Anchor.CENTER_LEFT
            padding = self.widget.config.padding.left
        coordinate = self.area.at_anchor(anchor) + padding
        found = False
        for i, child in enumerate(self._children):
            if not found:
                if i == self._selected_index:
                    found = True
                else:
                    continue
            anchored = child.anchored(coordinate, anchor)
            anchored_drawing = DrawingOnScreens(
                anchored._drawing_on_screens_without_parent
            )
            if (
                i != self._selected_index
                and anchored_drawing.rectangle_area_on_screen not in self.area
            ):
                break
            indexed_child = _IndexedChild(i, anchored)
            res.append(indexed_child)
            if self._is_vertical:
                coordinate += (
                    anchored_drawing.height + self.widget.config.padding.height
                )
            else:
                coordinate += (
                    anchored_drawing.width + self.widget.config.padding.width
                )
        return tuple(res)


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

    @cached_property
    def deselect(self) -> Self:
        return replace(self, child=self.child.deselect)

    @cached_property
    def select(self) -> Self:
        return replace(self, child=self.child.select)

    def tick(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        if res := self.child._tick_without_parent(time_delta, state):
            child, state = res
            ticked = replace(self, child=child)
        else:
            ticked = self
        return ticked, state
