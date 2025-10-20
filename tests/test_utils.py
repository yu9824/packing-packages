"""Tests for utils module."""

import inspect
import sys
from unittest.mock import patch

import pytest

from packing_packages.utils import (
    check_encoding,
    dummy_tqdm,
    is_argument,
    is_installed,
)


class TestIsInstalled:
    """Test is_installed function."""

    def test_is_installed_existing_package(self):
        """Test is_installed with existing package."""
        # sys is always available
        assert is_installed("sys") is True

    def test_is_installed_nonexistent_package(self):
        """Test is_installed with non-existent package."""
        assert is_installed("nonexistent_package_12345") is False

    def test_is_installed_empty_string(self):
        """Test is_installed with empty string."""
        assert is_installed("") is False


class TestIsArgument:
    """Test is_argument function."""

    def test_is_argument_existing_arg(self):
        """Test is_argument with existing argument."""

        def test_func(arg1, arg2, kwarg=None):
            pass

        assert is_argument(test_func, "arg1") is True
        assert is_argument(test_func, "arg2") is True
        assert is_argument(test_func, "kwarg") is True

    def test_is_argument_nonexistent_arg(self):
        """Test is_argument with non-existent argument."""

        def test_func(arg1):
            pass

        assert is_argument(test_func, "nonexistent") is False

    def test_is_argument_builtin_function(self):
        """Test is_argument with builtin function."""
        assert is_argument(len, "iterable") is True
        assert is_argument(len, "nonexistent") is False


class TestDummyTqdm:
    """Test dummy_tqdm class."""

    def test_dummy_tqdm_iteration(self):
        """Test dummy_tqdm iteration."""
        test_list = [1, 2, 3, 4, 5]
        dummy = dummy_tqdm(test_list)

        result = list(dummy)
        assert result == test_list

    def test_dummy_tqdm_attributes(self):
        """Test dummy_tqdm attribute access."""
        test_list = [1, 2, 3]
        dummy = dummy_tqdm(test_list)

        # Should not raise AttributeError
        dummy.set_description("test")
        dummy.update(1)
        dummy.close()

    def test_dummy_tqdm_no_operation(self):
        """Test that dummy_tqdm methods are no-ops."""
        test_list = [1, 2, 3]
        dummy = dummy_tqdm(test_list)

        # These should not raise exceptions
        dummy.set_description("test")
        dummy.update(1)
        dummy.close()
        dummy.refresh()


class TestCheckEncoding:
    """Test check_encoding function."""

    def test_check_encoding_default(self):
        """Test check_encoding with default encoding."""
        with patch("sys.getdefaultencoding", return_value="utf-8"):
            result = check_encoding(None)
            assert result == "utf-8"

    def test_check_encoding_valid_encoding(self):
        """Test check_encoding with valid encoding."""
        result = check_encoding("utf-8")
        assert result == "utf-8"

    def test_check_encoding_invalid_encoding(self):
        """Test check_encoding with invalid encoding."""
        with pytest.raises(ValueError, match="Invalid encoding"):
            check_encoding("invalid_encoding_12345")

    def test_check_encoding_ascii(self):
        """Test check_encoding with ascii encoding."""
        result = check_encoding("ascii")
        assert result == "ascii"

    def test_check_encoding_latin1(self):
        """Test check_encoding with latin1 encoding."""
        result = check_encoding("latin1")
        assert result == "latin1"
