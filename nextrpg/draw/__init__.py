"""
Drawing utilities and screen rendering for NextRPG.

This module provides comprehensive drawing and rendering functionality
for NextRPG games. It includes coordinate systems, text rendering,
animation frames, fade effects, and screen drawing operations.

The module contains several key components:
- `coordinate`: 2D coordinate system and positioning utilities
- `draw_on_screen`: Core drawing operations and screen rendering
- `text`: Text rendering and font management
- `text_on_screen`: On-screen text display and positioning
- `frames`: Animation frame management and sprite handling
- `fade_in`: Screen fade-in effects
- `fade_out`: Screen fade-out effects

These components work together to provide a complete rendering
system that supports sprites, text, animations, and visual effects.

Example:
    ```python
    from nextrpg.draw import coordinate, draw_on_screen, text

    # Create a coordinate
    pos = coordinate.Coordinate(100, 200)

    # Create a drawing
    drawing = draw_on_screen.Drawing(pos, size)

    # Render text
    text_drawing = text.Text("Hello World", font)
    ```
"""
