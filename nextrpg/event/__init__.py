"""
Event handling system for NextRPG.

This module provides a comprehensive event handling system for NextRPG
games. It includes pygame event processing, RPG-specific events,
dialog events, and event transformation utilities.

The event system includes:
- `pygame_event`: Pygame event processing and type conversion
- `rpg_event`: RPG-specific event types and handling
- `say_event`: Dialog and text event system
- `code_transformers`: Event code transformation utilities
- `event_as_attr`: Attribute-based event handling
- `event_transformer`: Event transformation utilities
- `plugins`: Event plugin system for extensibility

The event system is designed to provide a unified interface for
handling all types of game events, from user input to game-specific
events like dialog and RPG mechanics.

Example:
    ```python
    from nextrpg.event import pygame_event
    from nextrpg.event.rpg_event import RpgEvent
    from nextrpg.event.say_event import SayEvent

    # Handle pygame events
    event = pygame_event.to_typed_event(pygame_event)

    # Create RPG events
    rpg_event = RpgEvent("move", {"direction": "up"})

    # Handle dialog events
    say_event = SayEvent("Hello, world!")
    ```
"""
