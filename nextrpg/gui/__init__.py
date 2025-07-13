"""
GUI and window management system for NextRPG.

This module provides the graphical user interface and window management
system for NextRPG games. It includes window creation, area management,
and GUI component handling.

The GUI system includes:
- `window`: Main window management and pygame window handling
- `area`: GUI area management and layout utilities

The GUI system is responsible for:
- Creating and managing the game window
- Handling window events and resizing
- Managing GUI areas and layouts
- Coordinating with the drawing system
- Providing consistent GUI behavior across platforms

The system is designed to work seamlessly with pygame and provides
a clean abstraction for window management and GUI operations.

Example:
    ```python
    from nextrpg.gui import window, area

    # Create a window
    gui = window.Gui()

    # Handle window events
    gui = gui.event(pygame_event)

    # Draw content
    gui.draw(drawables, time_delta)
    ```
"""
