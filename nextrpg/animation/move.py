from dataclasses import dataclass

from nextrpg import Direction


@dataclass(frozen=True)
class Move:
    direction: Direction
