"""Integration tests for packing_packages."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from packing_packages import __version__
from packing_packages.__main__ import main as main_main
from packing_packages.install.__main__ import main as install_main
from packing_packages.pack.__main__ import main as pack_main
from packing_packages.pack.yaml.__main__ import main as yaml_main


class TestIntegration:
    """Integration tests for the entire package."""

    def test_package_version(self):
        """Test that package version is accessible."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_main_module_import(self):
        """Test that main module can be imported."""
        from packing_packages import __main__

        assert hasattr(__main__, "main")
        assert hasattr(__main__, "entrypoint")

    def test_pack_module_import(self):
        """Test that pack module can be imported."""
        from packing_packages.pack import __main__

        assert hasattr(__main__, "main")
        assert hasattr(__main__, "pack")

    def test_install_module_import(self):
        """Test that install module can be imported."""
        from packing_packages.install import __main__

        assert hasattr(__main__, "main")
        assert hasattr(__main__, "install")

    def test_yaml_module_import(self):
        """Test that yaml module can be imported."""
        from packing_packages.pack.yaml import __main__

        assert hasattr(__main__, "main")
        assert hasattr(__main__, "pack_from_yaml")

    def test_constants_import(self):
        """Test that constants can be imported."""
        from packing_packages.constants import (
            EXTENSIONS_CONDA,
            EXTENSIONS_PYPI,
        )

        assert EXTENSIONS_CONDA is not None
        assert EXTENSIONS_PYPI is not None

    def test_utils_import(self):
        """Test that utils can be imported."""
        from packing_packages.utils import check_encoding, is_installed

        assert callable(is_installed)
        assert callable(check_encoding)

    def test_logging_import(self):
        """Test that logging can be imported."""
        from packing_packages.logging import get_child_logger, get_root_logger

        assert callable(get_child_logger)
        assert callable(get_root_logger)


class TestMainIntegration:
    """Integration tests for main module."""

    def test_main_version(self):
        """Test main module version argument."""
        with pytest.raises(SystemExit):
            main_main(["-v"])

    def test_main_help(self):
        """Test main module help argument."""
        with pytest.raises(SystemExit):
            main_main(["--help"])

    def test_main_pack_help(self):
        """Test main module pack help."""
        with pytest.raises(SystemExit):
            main_main(["pack", "--help"])

    def test_main_install_help(self):
        """Test main module install help."""
        with pytest.raises(SystemExit):
            main_main(["install", "--help"])

    def test_main_pack_yaml_help(self):
        """Test main module pack yaml help."""
        with pytest.raises(SystemExit):
            main_main(["pack", "yaml", "--help"])


class TestPackIntegration:
    """Integration tests for pack module."""

    def test_pack_help(self):
        """Test pack module help."""
        with pytest.raises(SystemExit):
            pack_main(["--help"])

    def test_pack_dry_run(self):
        """Test pack module dry run."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
                with patch(
                    "packing_packages.pack._core.packing_packages"
                ) as mock_packing:
                    try:
                        pack_main(["-d", temp_dir, "-D"])
                    except SystemExit:
                        pass  # Expected for missing required arguments

    def test_pack_with_env_name(self):
        """Test pack module with environment name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "packing_packages.pack._core.packing_packages"
            ) as mock_packing:
                try:
                    pack_main(["-n", "test_env", "-d", temp_dir, "-D"])
                except SystemExit:
                    pass  # Expected for missing required arguments


class TestInstallIntegration:
    """Integration tests for install module."""

    def test_install_help(self):
        """Test install module help."""
        with pytest.raises(SystemExit):
            install_main(["--help"])

    def test_install_with_packages_dir(self):
        """Test install module with packages directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
                with patch(
                    "packing_packages.install._core.install_packages"
                ) as mock_install:
                    try:
                        install_main([temp_dir])
                    except SystemExit:
                        pass  # Expected for missing required arguments

    def test_install_with_env_name(self):
        """Test install module with environment name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "packing_packages.install._core.install_packages"
            ) as mock_install:
                try:
                    install_main([temp_dir, "-n", "test_env"])
                except SystemExit:
                    pass  # Expected for missing required arguments


class TestYamlIntegration:
    """Integration tests for yaml module."""

    def test_yaml_help(self):
        """Test yaml module help."""
        with pytest.raises(SystemExit):
            yaml_main(["--help"])

    def test_yaml_with_platform(self):
        """Test yaml module with platform."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "packing_packages.pack.yaml._core.packing_packages_from_yaml"
            ) as mock_packing:
                try:
                    yaml_main(["test.yaml", "-p", "linux-64", "-d", temp_dir])
                except SystemExit:
                    pass  # Expected for missing required arguments

    def test_yaml_dry_run(self):
        """Test yaml module dry run."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "packing_packages.pack.yaml._core.packing_packages_from_yaml"
            ) as mock_packing:
                try:
                    yaml_main(["test.yaml", "-d", temp_dir, "-D"])
                except SystemExit:
                    pass  # Expected for missing required arguments


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    def test_package_structure(self):
        """Test that package structure is correct."""
        # Test that all main modules exist
        assert Path("src/packing_packages/__init__.py").exists()
        assert Path("src/packing_packages/__main__.py").exists()
        assert Path("src/packing_packages/constants.py").exists()
        assert Path("src/packing_packages/pack/__main__.py").exists()
        assert Path("src/packing_packages/pack/_core.py").exists()
        assert Path("src/packing_packages/install/__main__.py").exists()
        assert Path("src/packing_packages/install/_core.py").exists()
        assert Path("src/packing_packages/pack/yaml/__main__.py").exists()
        assert Path("src/packing_packages/pack/yaml/_core.py").exists()
        assert Path("src/packing_packages/utils/_utils.py").exists()
        assert Path("src/packing_packages/logging/_logging.py").exists()

    def test_package_metadata(self):
        """Test that package metadata is accessible."""
        from packing_packages import __author__, __license__, __version__

        assert __version__ is not None
        assert __author__ is not None
        assert __license__ is not None

    def test_package_imports(self):
        """Test that all package imports work."""
        # Test main imports
        import packing_packages
        import packing_packages.constants
        import packing_packages.install
        import packing_packages.logging
        import packing_packages.pack
        import packing_packages.pack.yaml
        import packing_packages.utils

        # Test that modules are accessible
        assert hasattr(packing_packages, "__version__")
        assert hasattr(packing_packages.constants, "EXTENSIONS_CONDA")
        assert hasattr(packing_packages.constants, "EXTENSIONS_PYPI")
        assert hasattr(packing_packages.utils, "is_installed")
        assert hasattr(packing_packages.logging, "get_child_logger")

    def test_package_functionality(self):
        """Test that package functionality works."""
        from packing_packages.logging import get_child_logger
        from packing_packages.utils import check_encoding, is_installed

        # Test utility functions
        assert isinstance(is_installed("sys"), bool)
        assert isinstance(check_encoding("utf-8"), str)

        # Test logging
        logger = get_child_logger("test")
        assert logger is not None
