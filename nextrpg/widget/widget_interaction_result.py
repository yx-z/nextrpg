from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Self, override

from nextrpg.core.time import Millisecond
from nextrpg.event.user_event import UserEvent
from nextrpg.game.game_state import GameState
from nextrpg.scene.scene import Scene

if TYPE_CHECKING:
    from nextrpg.widget.widget import Widget
    from nextrpg.widget.widget_spec import WidgetSpec


class BaseWidgetInteractionResult(UserEvent):
    # Subclass shall have this member.
    target: Widget | None

    def with_target_if_not_set(self, widget: Widget) -> Self:
        if self.target:
            return self
        return replace(self, target=widget)


class _WidgetInteractionResultRequireTarget(BaseWidgetInteractionResult):
    @override
    def post(
        self, delay: Millisecond | Callable[[GameState], bool] = 0
    ) -> None:
        assert (
            self.target and self.target.spec.metadata
        ), f"Require target Widget with metadata. Got target {self.target}"
        super().post(delay)


@dataclass(frozen=True)
class AddChildWidget(BaseWidgetInteractionResult):
    widget_spec: WidgetSpec
    target: Widget | None = None


@dataclass(frozen=True)
class ReplaceByWidget(_WidgetInteractionResultRequireTarget):
    widget_spec: WidgetSpec
    target: Widget | None = None


type _Variant = Scene | BaseWidgetInteractionResult | None
type WidgetInteractionResult = _Variant | tuple[_Variant, GameState]
