from typing import ClassVar

from frozendict import frozendict

from nextrpg.animation.animation_spec import AnimationSpec
from nextrpg.animation.timed_animation_spec import TimedAnimationSpec
from nextrpg.core.dataclass_with_default import dataclass_with_default, default
from nextrpg.core.metadata import HasMetadata, Metadata
from nextrpg.scene.scene import Scene
from nextrpg.widget.widget import Widget


@dataclass_with_default(frozen=True)
class WidgetSpec[_Widget: Widget](HasMetadata):
    # Must be a subclass of Widget.
    widget_type: ClassVar[type]
    selectable: bool = True
    enter_animation: AnimationSpec | None = None
    exit_animation: AnimationSpec | None = default(
        lambda self: self._init_exit_animation
    )
    name: str | None = None
    metadata: Metadata = ()

    def match_metadata(self, other: Widget | WidgetSpec | Metadata) -> bool:
        match other:
            case Widget():
                metadata = other.spec.metadata
            case WidgetSpec():
                metadata = other.metadata
            case _:
                metadata = other
        return self.metadata == metadata

    def with_parent(self, parent: Scene | None) -> _Widget:
        if isinstance(parent, Widget):
            name_to_on_screens = parent.name_to_on_screens
        else:
            name_to_on_screens = frozendict()
        return self.widget_type(
            spec=self, name_to_on_screens=name_to_on_screens, parent=parent
        )

    @property
    def _init_exit_animation(self) -> AnimationSpec | None:
        if isinstance(self.enter_animation, TimedAnimationSpec):
            return self.enter_animation.reversed
        return None
