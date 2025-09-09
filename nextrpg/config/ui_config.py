from dataclasses import dataclass
from typing import TYPE_CHECKING

from nextrpg.drawing.color import Color
from nextrpg.geometry.dimension import Pixel
from nextrpg.geometry.rectangle_area_on_screen import RectangleAreaOnScreen
from nextrpg.scene.widget.scroll_direction import ScrollDirection

if TYPE_CHECKING:
    from nextrpg.drawing.drawing_on_screen import DrawingOnScreen
    from nextrpg.drawing.nine_slice import NineSlice


@dataclass(frozen=True)
class PanelConfig:
    padding: Pixel = 8
    background: NineSlice | Color | None = None
    scroll_direction: ScrollDirection = ScrollDirection.VERTICAL

    def drawing_on_screens(
        self, area: RectangleAreaOnScreen
    ) -> tuple[DrawingOnScreen, ...]:
        from nextrpg.drawing.nine_slice import NineSlice

        if not self.background:
            return ()
        if isinstance(self.background, NineSlice):
            return self.background.stretch(area.size).drawing_on_screens(
                area.top_left
            )
        return (area.fill(self.background),)


@dataclass(frozen=True)
class UiConfig:
    panel: PanelConfig = PanelConfig()
