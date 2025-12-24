from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SaveConfig:
    directory: Path = Path.home() / "nextrpg"
    shared_slot: str = "shared"
    text_file: str = "save.json"
    key_delimiter: str = "|"
    time_format: str = "%Y-%m-%d %H:%M:%S"
