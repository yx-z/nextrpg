from ast import NodeTransformer
from dataclasses import dataclass

from nextrpg.code_transformers import ADD_PARENT, ADD_YIELD, ANNOTATE_SAY


@dataclass(frozen=True)
class EventConfig:
    transformers: tuple[NodeTransformer] = (ADD_PARENT, ANNOTATE_SAY, ADD_YIELD)
