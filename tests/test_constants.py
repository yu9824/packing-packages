"""Tests for constants module."""

import pytest

from packing_packages.constants import EXTENSIONS_CONDA, EXTENSIONS_PYPI


class TestConstants:
    """Test constants module."""

    def test_extensions_conda(self):
        """Test EXTENSIONS_CONDA constant."""
        assert isinstance(EXTENSIONS_CONDA, tuple)
        assert len(EXTENSIONS_CONDA) == 2
        assert "tar.bz2" in EXTENSIONS_CONDA
        assert "conda" in EXTENSIONS_CONDA

    def test_extensions_pypi(self):
        """Test EXTENSIONS_PYPI constant."""
        assert isinstance(EXTENSIONS_PYPI, tuple)
        assert len(EXTENSIONS_PYPI) == 2
        assert "whl" in EXTENSIONS_PYPI
        assert "tar.gz" in EXTENSIONS_PYPI

    def test_extensions_conda_immutable(self):
        """Test that EXTENSIONS_CONDA is immutable."""
        with pytest.raises(AttributeError):
            EXTENSIONS_CONDA.append("new_ext")  # type: ignore[attr-defined]

    def test_extensions_pypi_immutable(self):
        """Test that EXTENSIONS_PYPI is immutable."""
        with pytest.raises(AttributeError):
            EXTENSIONS_PYPI.append("new_ext")  # type: ignore[attr-defined]
