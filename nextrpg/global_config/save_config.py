from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SaveConfig:
    directory: Path = Path.home() / "nextrpg"
