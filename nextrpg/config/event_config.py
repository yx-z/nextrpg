from ast import NodeTransformer
from dataclasses import dataclass
from types import ModuleType

from nextrpg.event import plugins
from nextrpg.event.code_transformers import ADD_PARENT, ADD_YIELD, ANNOTATE_SAY


@dataclass(frozen=True)
class EventConfig:
    modules: tuple[ModuleType] = (plugins,)
    transformers: tuple[NodeTransformer] = (ADD_PARENT, ANNOTATE_SAY, ADD_YIELD)
