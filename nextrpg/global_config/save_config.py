from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SaveConfig:
    directory: Path = Path.home() / "nextrpg"
    shared_slot: str = "shared"
    text_save_file: str = "text_save_file"
