from dataclasses import dataclass

from nextrpg.common_types import Size


@dataclass(frozen=True)
class GuiConfig:
    title: str = "NextRPG"
    size: Size = Size(width=1280, height=800)
    frames_per_second: int = 60
    allow_resize: bool = True


@dataclass(frozen=True)
class MapConfig:
    background_layer_prefix: str = "background"
    foreground_layer_prefix: str = "foreground"
    collision_layer_prefix: str = "collision"
    player_layer: str = "player"
    character_direction_property_name = "direction"


@dataclass(frozen=True)
class Config:
    gui: GuiConfig = GuiConfig()
    map: MapConfig = MapConfig()
