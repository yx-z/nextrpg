from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from nextrpg import DrawingOnScreen
from nextrpg.core.tmx_loader import TmxLoader
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class TitleScene(Scene):
    tmx_file: Path

    @cached_property
    def drawing_on_screens(self) -> tuple[DrawingOnScreen, ...]:
        return (self._tmx.image_layer("background"),)

    @cached_property
    def _tmx(self) -> TmxLoader:
        return TmxLoader(self.tmx_file)
