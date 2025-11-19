from dataclasses import dataclass
from pathlib import Path

from nextrpg.game.game_save_meta import GameSaveMeta


@dataclass(frozen=True)
class SaveConfig:
    directory: Path = Path.home() / "nextrpg"
    shared_slot: str = "shared"
    text_file: str = "save.json"
    key_delimiter: str = "|"
    time_format: str = "%Y-%m-%d %H:%M:%S"
    save_meta_type: type[GameSaveMeta] = GameSaveMeta
