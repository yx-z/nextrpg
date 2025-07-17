"""
Event configuration system for `nextrpg`.

This module provides configuration options for event processing in `nextrpg`
games. It includes the `EventConfig` class which defines code transformers for
event handling and processing.

Features:
    - Code transformer configuration
    - Event processing pipeline setup
    - Integration with code transformation system
"""

from ast import NodeTransformer
from dataclasses import dataclass

from nextrpg.event.code_transformers import ADD_PARENT, ADD_YIELD, ANNOTATE_SAY


@dataclass(frozen=True)
class EventConfig:
    """
    Configuration class for event processing.

    This global_config defines the code transformers used for processing events in
    `nextrpg` games. These transformers modify the AST to add event handling
    capabilities.

    Arguments:
        transformers: Tuple of AST node transformers to apply during event
            processing. Defaults to a standard set of transformers for parent
            addition, say annotation, and yield addition.
    """

    transformers: tuple[NodeTransformer] = (ADD_PARENT, ANNOTATE_SAY, ADD_YIELD)
