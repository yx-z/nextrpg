from dataclasses import dataclass

from nextrpg.draw.drawing import Drawing
from nextrpg.draw.drawing_group import DrawingGroup
from nextrpg.scene.scene import Scene


@dataclass(frozen=True)
class Button:
    idle: Drawing | DrawingGroup
    selected: Drawing | DrawingGroup
    click: Scene
