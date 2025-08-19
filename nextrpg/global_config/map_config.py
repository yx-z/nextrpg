from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MapConfig:
    background: str = "background"
    foreground: str = "foreground"
    above_character: str = "above_character"
    collision: str = "collision"
    cache_size: int = 8
