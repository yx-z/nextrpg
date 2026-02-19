"""
Shared test utilities and mock objects for nextrpg tests.

This module provides common stubs, mocks, and fixtures to avoid 
initializing pygame surfaces and other heavy dependencies in tests.
"""

from unittest.mock import MagicMock, Mock, patch
from dataclasses import dataclass, field
from typing import Any


# ============================================================================
# Mock pygame objects without initializing pygame display
# ============================================================================


def create_mock_surface(width: int = 100, height: int = 100) -> MagicMock:
    """
    Create a mock pygame Surface without initializing pygame.
    
    Args:
        width: Width of the mock surface
        height: Height of the mock surface
    
    Returns:
        A configured MagicMock representing a pygame Surface
    """
    surface = MagicMock()
    surface.get_size.return_value = (width, height)
    surface.get_width.return_value = width
    surface.get_height.return_value = height
    surface.get_rect.return_value.width = width
    surface.get_rect.return_value.height = height
    surface.copy.return_value = surface
    surface.fill.return_value = None
    surface.blit.return_value = None
    return surface


def create_mock_color(r: int = 255, g: int = 255, b: int = 255, a: int = 255) -> MagicMock:
    """
    Create a mock pygame Color object.
    
    Args:
        r, g, b, a: Color components (0-255)
    
    Returns:
        A configured MagicMock representing a pygame Color
    """
    color = MagicMock()
    color.r = r
    color.g = g
    color.b = b
    color.a = a
    return color


def create_mock_rect(x: int = 0, y: int = 0, width: int = 100, height: int = 100) -> MagicMock:
    """
    Create a mock pygame Rect object.
    
    Args:
        x, y: Position coordinates
        width, height: Dimensions
    
    Returns:
        A configured MagicMock representing a pygame Rect
    """
    rect = MagicMock()
    rect.x = x
    rect.y = y
    rect.width = width
    rect.height = height
    rect.left = x
    rect.top = y
    rect.right = x + width
    rect.bottom = y + height
    rect.centerx = x + width // 2
    rect.centery = y + height // 2
    rect.size = (width, height)
    rect.copy.return_value = rect
    return rect


def create_mock_font(name: str = "Arial", size: int = 12) -> MagicMock:
    """
    Create a mock pygame Font object.
    
    Args:
        name: Font name
        size: Font size
    
    Returns:
        A configured MagicMock representing a pygame Font
    """
    font = MagicMock()
    font.name = name
    font.size = size
    surface = create_mock_surface(len(name) * size // 2, size)
    font.render.return_value = surface
    return font


# ============================================================================
# Configuration mocks
# ============================================================================


@dataclass
class MockAudioConfig:
    """Mock audio configuration."""
    volume: float = 1.0
    max_channels: int = 8


@dataclass
class MockSystemConfig:
    """Mock system configuration."""
    background_thread_count: int = 4


@dataclass
class MockConfig:
    """Mock nextrpg configuration."""
    system: Any = field(default_factory=lambda: MagicMock())
    
    def __post_init__(self):
        if not hasattr(self.system, 'resource'):
            resource_mock = MagicMock()
            resource_mock.background_thread_count = 4
            self.system.resource = resource_mock
        if not hasattr(self.system, 'audio'):
            self.system.audio = MockAudioConfig()
        if not hasattr(self.system, 'sound'):
            self.system.sound = MockAudioConfig()


def mock_config() -> MockConfig:
    """
    Create a properly configured mock config object.
    
    Returns:
        A MockConfig instance with sensible defaults
    """
    return MockConfig(system=MagicMock(
        resource=MagicMock(background_thread_count=4),
        audio=MockAudioConfig(),
        sound=MockAudioConfig()
    ))


# ============================================================================
# Time-related stubs
# ============================================================================


class MockTimer:
    """Simple mock timer for testing time-based logic."""
    
    def __init__(self, duration: int = 1000):
        self.duration = duration
        self.elapsed = 0
    
    def tick(self, delta: int) -> 'MockTimer':
        """Advance time by delta milliseconds."""
        new_timer = MockTimer(self.duration)
        new_timer.elapsed = self.elapsed + delta
        return new_timer
    
    @property
    def is_complete(self) -> bool:
        """Check if timer has completed."""
        return self.elapsed >= self.duration
    
    @property
    def remaining(self) -> int:
        """Get remaining time."""
        return max(0, self.duration - self.elapsed)
    
    @property
    def completed_percentage(self) -> float:
        """Get completion as percentage (0.0-1.0)."""
        return min(1.0, self.elapsed / self.duration)


# ============================================================================
# Coordinate and geometry stubs
# ============================================================================


@dataclass
class MockCoordinate:
    """Mock coordinate for testing."""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other: 'MockCoordinate') -> 'MockCoordinate':
        if isinstance(other, MockCoordinate):
            return MockCoordinate(self.x + other.x, self.y + other.y)
        return NotImplemented
    
    def __sub__(self, other: 'MockCoordinate') -> 'MockCoordinate':
        if isinstance(other, MockCoordinate):
            return MockCoordinate(self.x - other.x, self.y - other.y)
        return NotImplemented


@dataclass
class MockSize:
    """Mock size for testing."""
    width: float = 100.0
    height: float = 100.0


@dataclass
class MockDimension:
    """Mock dimension for testing."""
    value: float = 100.0
    
    def __mul__(self, other: float) -> 'MockDimension':
        return MockDimension(self.value * other)
    
    def __truediv__(self, other: float) -> 'MockDimension':
        return MockDimension(self.value / other)


# ============================================================================
# Animation and sprite stubs
# ============================================================================


class MockSprite:
    """Mock sprite for testing animation."""
    
    def __init__(self, width: int = 100, height: int = 100):
        self.surface = create_mock_surface(width, height)
        self.width = width
        self.height = height
        self.is_complete = False
    
    @property
    def pygame(self):
        """Return mock pygame surface."""
        return self.surface


class MockAnimationSpec:
    """Mock animation specification."""
    
    def __init__(self, duration: int = 1000):
        self.duration = duration


# ============================================================================
# Audio stubs
# ============================================================================


class MockSoundSpec:
    """Mock sound specification."""
    
    def __init__(self, path: str = "mock.wav", loop: bool = False):
        self.path = path
        self.loop = loop
        self.volume = 1.0


class MockMusicSpec:
    """Mock music specification."""
    
    def __init__(self, path: str = "mock.ogg"):
        self.path = path


# ============================================================================
# Character stubs
# ============================================================================


class MockCharacterSpec:
    """Mock character specification."""
    
    def __init__(self, name: str = "TestChar"):
        self.name = name
        self.x = 0
        self.y = 0


class MockPlayerSpec:
    """Mock player specification."""
    
    def __init__(self, name: str = "Player"):
        self.name = name


class MockNPCSpec:
    """Mock NPC specification."""
    
    def __init__(self, name: str = "NPC"):
        self.name = name


# ============================================================================
# Item stubs
# ============================================================================


class MockItemSpec:
    """Mock item specification."""
    
    def __init__(self, name: str = "Item", value: int = 1):
        self.name = name
        self.value = value


# ============================================================================
# Patching utilities
# ============================================================================


def patch_pygame_surface():
    """
    Decorator/context manager to mock pygame.Surface initialization.
    
    Usage:
        @patch_pygame_surface()
        def test_something():
            ...
    """
    return patch('pygame.Surface', side_effect=create_mock_surface)


def patch_config():
    """
    Decorator/context manager to mock nextrpg.config.config.config.
    
    Usage:
        @patch_config()
        def test_something():
            ...
    """
    return patch('nextrpg.config.config.config', return_value=mock_config())


def patch_get_timepoint():
    """
    Decorator/context manager to mock pygame.time.get_ticks.
    
    Usage:
        @patch_get_timepoint()
        def test_something():
            ...
    """
    return patch('pygame.time.get_ticks', return_value=0)
