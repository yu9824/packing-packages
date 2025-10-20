"""Tests for logging module."""

import os
import sys
from logging import Logger, StreamHandler
from unittest.mock import patch

import pytest

from packing_packages.logging import (
    _color_supported,
    _get_root_logger_name,
    catch_default_handler,
    create_default_formatter,
    disable_default_handler,
    enable_default_handler,
    get_child_logger,
    get_handler,
    get_root_logger,
)


class TestColorSupported:
    """Test _color_supported function."""

    def test_color_supported_no_colorlog(self):
        """Test _color_supported when colorlog is not available."""
        with patch("importlib.util.find_spec", return_value=None):
            assert _color_supported() is False

    def test_color_supported_no_color_env(self):
        """Test _color_supported when NO_COLOR is set."""
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            with patch("importlib.util.find_spec", return_value=object()):
                assert _color_supported() is False

    def test_color_supported_no_tty(self):
        """Test _color_supported when stderr is not a tty."""
        with patch("importlib.util.find_spec", return_value=object()):
            with patch.dict(os.environ, {}, clear=True):
                with patch.object(sys.stderr, "isatty", return_value=False):
                    assert _color_supported() is False

    def test_color_supported_available(self):
        """Test _color_supported when colorlog is available and conditions are met."""
        with patch("importlib.util.find_spec", return_value=object()):
            with patch.dict(os.environ, {}, clear=True):
                with patch.object(sys.stderr, "isatty", return_value=True):
                    assert _color_supported() is True


class TestGetRootLoggerName:
    """Test _get_root_logger_name function."""

    def test_get_root_logger_name(self):
        """Test _get_root_logger_name returns correct name."""
        # This should return the first part of the module name
        with patch(
            "packing_packages.logging.__name__",
            "packing_packages.logging._logging",
        ):
            result = _get_root_logger_name()
            assert result == "packing_packages"


class TestCreateDefaultFormatter:
    """Test create_default_formatter function."""

    def test_create_default_formatter_with_color(self):
        """Test create_default_formatter with color support."""
        with patch(
            "packing_packages.logging._color_supported", return_value=True
        ):
            with patch("colorlog.ColoredFormatter") as mock_colored:
                formatter = create_default_formatter()
                mock_colored.assert_called_once()

    def test_create_default_formatter_without_color(self):
        """Test create_default_formatter without color support."""
        with patch(
            "packing_packages.logging._color_supported", return_value=False
        ):
            formatter = create_default_formatter()
            assert formatter is not None


class TestGetHandler:
    """Test get_handler function."""

    def test_get_handler_basic(self):
        """Test get_handler with basic parameters."""
        handler = StreamHandler()
        result = get_handler(handler)

        assert result is handler
        assert handler.formatter is not None

    def test_get_handler_with_formatter(self):
        """Test get_handler with custom formatter."""
        from logging import Formatter

        handler = StreamHandler()
        custom_formatter = Formatter("custom")
        result = get_handler(handler, formatter=custom_formatter)

        assert result is handler
        assert handler.formatter is custom_formatter


class TestGetRootLogger:
    """Test get_root_logger function."""

    def test_get_root_logger(self):
        """Test get_root_logger returns a logger."""
        logger = get_root_logger()
        assert isinstance(logger, Logger)


class TestGetChildLogger:
    """Test get_child_logger function."""

    def test_get_child_logger_valid_name(self):
        """Test get_child_logger with valid name."""
        logger = get_child_logger("packing_packages.test_module")
        assert isinstance(logger, Logger)

    def test_get_child_logger_main(self):
        """Test get_child_logger with __main__."""
        logger = get_child_logger("__main__")
        assert isinstance(logger, Logger)

    def test_get_child_logger_invalid_name(self):
        """Test get_child_logger with invalid name."""
        with pytest.raises(ValueError, match="You should use '__name__'."):
            get_child_logger("invalid_name")

    def test_get_child_logger_propagate(self):
        """Test get_child_logger propagate parameter."""
        logger = get_child_logger("packing_packages.test", propagate=False)
        assert logger.propagate is False


class TestHandlerControl:
    """Test handler enable/disable functions."""

    def test_enable_disable_handler(self):
        """Test enable and disable default handler."""
        # These should not raise exceptions
        enable_default_handler()
        disable_default_handler()


class TestCatchDefaultHandler:
    """Test catch_default_handler context manager."""

    def test_catch_default_handler_context(self):
        """Test catch_default_handler as context manager."""
        with catch_default_handler():
            # Should not raise exceptions
            pass

    def test_catch_default_handler_nested(self):
        """Test catch_default_handler with nested usage."""
        with catch_default_handler():
            with catch_default_handler():
                # Should not raise exceptions
                pass
