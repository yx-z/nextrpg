from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SaveConfig:
    directory: Path = Path.home() / "nextrpg"
    shared: Path = Path("shared")
    slot_pattern: str = "save_{slot}"

    def slot(self, slot: Any) -> Path:
        return Path(self.slot_pattern.format(slot=slot))
