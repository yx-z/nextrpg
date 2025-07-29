from dataclasses import dataclass


@dataclass(frozen=True)
class TileMapConfig:
    background: str = "background"
    foreground: str = "foreground"
    above_character: str = "above_character"
    collision: str = "collision"
