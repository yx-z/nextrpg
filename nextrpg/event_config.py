"""
Event configuration system for NextRPG.

This module provides configuration options for event processing
in NextRPG games. It includes the `EventConfig` class which
defines code transformers for event handling and processing.

The event configuration features:
- Code transformer configuration
- Event processing pipeline setup
- Integration with code transformation system

Example:
    ```python
    from nextrpg.event_config import EventConfig
    from nextrpg.code_transformers import ADD_PARENT, ADD_YIELD

    # Create default event config
    config = EventConfig()

    # Create custom event config
    custom_config = EventConfig(transformers=(ADD_PARENT, ADD_YIELD))
    ```
"""

from ast import NodeTransformer
from dataclasses import dataclass

from nextrpg.code_transformers import ADD_PARENT, ADD_YIELD, ANNOTATE_SAY


@dataclass(frozen=True)
class EventConfig:
    """
    Configuration class for event processing.

    This config defines the code transformers used for processing
    events in NextRPG games. These transformers modify the AST
    to add event handling capabilities.

    Arguments:
        `transformers`: Tuple of AST node transformers to apply
            during event processing. Defaults to a standard set
            of transformers for parent addition, say annotation,
            and yield addition.

    Example:
        ```python
        from nextrpg.event_config import EventConfig
        from nextrpg.code_transformers import ADD_PARENT, ADD_YIELD

        # Default configuration
        config = EventConfig()

        # Custom configuration with specific transformers
        custom_config = EventConfig(transformers=(ADD_PARENT, ADD_YIELD))
        ```
    """

    transformers: tuple[NodeTransformer] = (ADD_PARENT, ANNOTATE_SAY, ADD_YIELD)
