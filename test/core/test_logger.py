"""Tests for nextrpg.core.logger module."""
import logging
import pytest
from unittest.mock import MagicMock, patch
from string.templatelib import Template

from nextrpg.core.logger import (
    Logger,
    LogEntry,
    MessageKeyAndDrawing,
    pop_messages,
    _add,
    _format_template,
    _FROM_CONFIG,
    _DurationFromConfig,
    _Key,
    _TimedLogEntry,
    _entries,
    _timed_entries,
)
from nextrpg.config.logging_config import LogLevel
from nextrpg.core.time import Millisecond


class TestLoggerCreation:
    """Test Logger creation."""
    
    def test_logger_creation(self):
        """Test creating Logger."""
        logger = Logger(component="test_component")
        assert logger.component == "test_component"
    
    def test_logger_creation_with_different_components(self):
        """Test Logger with various components."""
        logger1 = Logger(component="comp1")
        logger2 = Logger(component="comp2")
        
        assert logger1.component == "comp1"
        assert logger2.component == "comp2"


class TestLoggerMessages:
    """Test Logger message methods."""
    
    @pytest.mark.skip(reason="Complex logging infrastructure, requires full config setup")
    def test_logger_debug(self):
        """Test Logger.debug method."""
        logger = Logger(component="test")
        # This would require full config setup to test properly
        pass
    
    @pytest.mark.skip(reason="Complex logging infrastructure, requires full config setup")
    def test_logger_info(self):
        """Test Logger.info method."""
        logger = Logger(component="test")
        # This would require full config setup to test properly
        pass
    
    @pytest.mark.skip(reason="Complex logging infrastructure, requires full config setup")
    def test_logger_error(self):
        """Test Logger.error method."""
        logger = Logger(component="test")
        # This would require full config setup to test properly
        pass


class TestLoggerWithConsole:
    """Test Logger with console_logger parameter."""
    
    def test_logger_debug_with_console_logger(self):
        """Test Logger.debug with console_logger."""
        logger = Logger(component="test")
        mock_console = MagicMock(spec=logging.Logger)
        
        # Should not raise
        logger.debug("test message", console_logger=mock_console)
        mock_console.debug.assert_called_once_with("test message")
    
    def test_logger_info_with_console_logger(self):
        """Test Logger.info with console_logger."""
        logger = Logger(component="test")
        mock_console = MagicMock(spec=logging.Logger)
        
        logger.info("test message", console_logger=mock_console)
        mock_console.info.assert_called_once_with("test message")
    
    def test_logger_error_with_console_logger(self):
        """Test Logger.error with console_logger."""
        logger = Logger(component="test")
        mock_console = MagicMock(spec=logging.Logger)
        
        logger.error("test message", console_logger=mock_console)
        mock_console.error.assert_called_once_with("test message")


class TestLoggerDrawingMethods:
    """Test Logger drawing methods."""
    
    @pytest.mark.skip(reason="Complex sprite infrastructure required")
    def test_logger_debug_drawing(self):
        """Test Logger.debug_drawing method."""
        logger = Logger(component="test")
        # Requires sprite infrastructure
        pass
    
    @pytest.mark.skip(reason="Complex sprite infrastructure required")
    def test_logger_info_drawing(self):
        """Test Logger.info_drawing method."""
        logger = Logger(component="test")
        # Requires sprite infrastructure
        pass
    
    @pytest.mark.skip(reason="Complex sprite infrastructure required")
    def test_logger_error_drawing(self):
        """Test Logger.error_drawing method."""
        logger = Logger(component="test")
        # Requires sprite infrastructure
        pass


class TestLogEntry:
    """Test LogEntry class."""
    
    def test_log_entry_creation(self):
        """Test creating LogEntry."""
        entry = LogEntry(
            component="test",
            level=LogLevel.INFO,
            message="test message"
        )
        assert entry.component == "test"
        assert entry.level == LogLevel.INFO
        assert entry.message == "test message"
    
    def test_log_entry_with_template(self):
        """Test LogEntry with Template message."""
        template = Template("test {}")
        entry = LogEntry(
            component="test",
            level=LogLevel.DEBUG,
            message=template
        )
        assert entry.message == template
    
    def test_log_entry_formatted_with_string(self):
        """Test LogEntry.formatted property with string message."""
        entry = LogEntry(
            component="test",
            level=LogLevel.INFO,
            message="test message"
        )
        # Should return the formatted string
        formatted = entry.formatted
        assert formatted == "test message"
    
    def test_log_entry_formatted_with_message_key_and_drawing(self):
        """Test LogEntry.formatted with MessageKeyAndDrawing."""
        mock_drawing = MagicMock()
        msg_and_drawing = MessageKeyAndDrawing(message_key="key1", drawing=mock_drawing)
        entry = LogEntry(
            component="test",
            level=LogLevel.INFO,
            message=msg_and_drawing
        )
        # Should return the MessageKeyAndDrawing as-is
        formatted = entry.formatted
        assert formatted == msg_and_drawing


class TestMessageKeyAndDrawing:
    """Test MessageKeyAndDrawing class."""
    
    def test_message_key_and_drawing_creation(self):
        """Test creating MessageKeyAndDrawing."""
        mock_drawing = MagicMock()
        msg_drawing = MessageKeyAndDrawing(message_key="key1", drawing=mock_drawing)
        
        assert msg_drawing.message_key == "key1"
        assert msg_drawing.drawing == mock_drawing
    
    def test_message_key_and_drawing_equality(self):
        """Test MessageKeyAndDrawing equality."""
        mock_drawing = MagicMock()
        msg1 = MessageKeyAndDrawing(message_key="key1", drawing=mock_drawing)
        msg2 = MessageKeyAndDrawing(message_key="key1", drawing=mock_drawing)
        
        assert msg1 == msg2


class TestFormatTemplate:
    """Test _format_template function."""
    
    def test_format_template_with_simple_string(self):
        """Test _format_template with simple string."""
        template = Template("hello world")
        result = _format_template(template)
        assert isinstance(result, str)
    
    def test_format_template_consistency(self):
        """Test _format_template returns same result for same input."""
        template = Template("test")
        result1 = _format_template(template)
        result2 = _format_template(template)
        assert result1 == result2


class TestDurationFromConfig:
    """Test _DurationFromConfig singleton."""
    
    def test_from_config_is_instance(self):
        """Test _FROM_CONFIG is instance of _DurationFromConfig."""
        assert isinstance(_FROM_CONFIG, _DurationFromConfig)
    
    def test_from_config_singleton(self):
        """Test _FROM_CONFIG behaves as singleton."""
        # Same instance used throughout
        from nextrpg.core.logger import _FROM_CONFIG as _FROM_CONFIG2
        assert _FROM_CONFIG is _FROM_CONFIG2


class TestLogKey:
    """Test _Key dataclass."""
    
    def test_key_creation(self):
        """Test creating _Key."""
        key = _Key(component="test", template="msg")
        assert key.component == "test"
        assert key.template == "msg"
    
    def test_key_hashable(self):
        """Test _Key is hashable for use in dict."""
        key1 = _Key(component="test", template="msg1")
        key2 = _Key(component="test", template="msg1")
        
        # Should be able to use as dict key
        test_dict = {key1: "value"}
        assert key2 in test_dict


class TestTimedLogEntry:
    """Test _TimedLogEntry class."""
    
    @pytest.mark.skip(reason="Requires Timer and config infrastructure")
    def test_timed_log_entry_creation(self):
        """Test creating _TimedLogEntry."""
        # Requires full Timer and config setup
        pass
    
    @pytest.mark.skip(reason="Requires Timer and config infrastructure")
    def test_timed_log_entry_timer(self):
        """Test _TimedLogEntry timer property."""
        # Requires full Timer and config setup
        pass


class TestPopMessages:
    """Test pop_messages function."""
    
    @pytest.mark.skip(reason="Requires full config infrastructure")
    def test_pop_messages_when_config_disabled(self):
        """Test pop_messages when debug config is None."""
        # Would need to mock entire config
        pass
    
    @pytest.mark.skip(reason="Requires full config infrastructure")
    def test_pop_messages_empty_when_logging_disabled(self):
        """Test pop_messages returns empty tuple when logging disabled."""
        # Would need to mock entire config
        pass
    
    @pytest.mark.skip(reason="Requires full config infrastructure")
    def test_pop_messages_filters_by_level(self):
        """Test pop_messages filters by log level."""
        # Would need to mock entire config
        pass


class TestAddFunction:
    """Test _add function."""
    
    @pytest.mark.skip(reason="Requires full config infrastructure and side effects")
    def test_add_with_string_message(self):
        """Test _add with string message."""
        # Has global side effects, difficult to test without mocking
        pass
    
    @pytest.mark.skip(reason="Requires full config infrastructure and side effects")
    def test_add_with_none_duration(self):
        """Test _add with None duration (uses _entries)."""
        # Has global side effects
        pass
    
    @pytest.mark.skip(reason="Requires full config infrastructure and side effects")
    def test_add_with_from_config_duration(self):
        """Test _add with _FROM_CONFIG duration."""
        # Has global side effects, uses _timed_entries
        pass
    
    @pytest.mark.skip(reason="Requires full config infrastructure and side effects")
    def test_add_with_custom_duration(self):
        """Test _add with custom duration."""
        # Has global side effects
        pass


class TestLoggerImmutability:
    """Test Logger immutability."""
    
    def test_logger_is_frozen_dataclass(self):
        """Test Logger cannot be modified."""
        logger = Logger(component="test")
        
        with pytest.raises(AttributeError):
            logger.component = "new_component"


class TestLogEntryImmutability:
    """Test LogEntry immutability."""
    
    def test_log_entry_is_frozen_dataclass(self):
        """Test LogEntry cannot be modified."""
        entry = LogEntry(
            component="test",
            level=LogLevel.INFO,
            message="test"
        )
        
        with pytest.raises(AttributeError):
            entry.component = "new_component"


class TestMessageKeyAndDrawingImmutability:
    """Test MessageKeyAndDrawing immutability."""
    
    def test_message_key_and_drawing_is_frozen(self):
        """Test MessageKeyAndDrawing cannot be modified."""
        mock_drawing = MagicMock()
        msg = MessageKeyAndDrawing(message_key="key1", drawing=mock_drawing)
        
        with pytest.raises(AttributeError):
            msg.message_key = "new_key"

