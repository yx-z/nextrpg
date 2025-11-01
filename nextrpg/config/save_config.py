from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SaveConfig:
    directory: Path = Path.home() / "nextrpg"
    shared_slot: str = "shared"
    text_save_file: str = "text_save_file"
    save_key_delimiter: str = "|"
    save_time_str_format: str = "%Y-%m-%d %H:%M:%S"
