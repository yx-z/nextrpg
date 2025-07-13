"""
Character drawing and movement systems for NextRPG.

This module provides comprehensive character management functionality
for NextRPG games. It includes character drawing interfaces, movement
systems, NPC management, and player character handling.

The module contains several key components:
- `CharacterDrawing`: Abstract interface for character rendering
- `CharacterOnScreen`: Character positioning and screen display
- `MovingCharacterOnScreen`: Animated character movement
- `PlayerOnScreen`: Player character specific functionality
- `MovingNpc`: NPC movement and behavior
- `Npcs`: NPC management and interaction systems
- `RpgMakerCharacterDrawing`: RPG Maker style character sprites

These components work together to provide a complete character system
that supports both player characters and NPCs with various movement
patterns and rendering styles.

Example:
    ```python
    from nextrpg.character import CharacterDrawing, Direction
    from nextrpg.character.rpg_maker_character_drawing import RpgMakerCharacterDrawing

    # Create a character drawing
    character = RpgMakerCharacterDrawing("sprites/player.png", Direction.DOWN)

    # Update character animation
    character = character.tick_idle(time_delta)
    ```
"""
