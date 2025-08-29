from ast import NodeTransformer
from dataclasses import dataclass

from nextrpg.event.code_transformer import (
    ADD_PARENT,
    ADD_YIELD,
    ANNOTATE_SAY,
    TRANSFORM_EVENT,
)


@dataclass(frozen=True)
class EventConfig:
    transformers: tuple[NodeTransformer] = (
        ADD_PARENT,
        ANNOTATE_SAY,
        ADD_YIELD,
        TRANSFORM_EVENT,
    )
