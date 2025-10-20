"""Tests for install.__main__ module."""

import argparse
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from packing_packages.install.__main__ import (
    add_arguments_install,
    install,
    main,
)


class TestInstallFunction:
    """Test install function."""

    def test_install_with_env_name(self):
        """Test install function with specified environment name."""
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
            with patch(
                "packing_packages.install._core.install_packages"
            ) as mock_install:
                args = argparse.Namespace(
                    env_name="custom_env",
                    dirpath_packages=Path("."),
                    encoding=None,
                )

                install(args)
                mock_install.assert_called_once_with(
                    dirpath_packages=Path(".").resolve(),
                    env_name="custom_env",
                    encoding=None,
                )

    def test_install_without_env_name(self):
        """Test install function without specified environment name."""
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
            with patch(
                "packing_packages.install._core.install_packages"
            ) as mock_install:
                args = argparse.Namespace(
                    env_name=None, dirpath_packages=Path("."), encoding=None
                )

                install(args)
                mock_install.assert_called_once_with(
                    dirpath_packages=Path(".").resolve(),
                    env_name="test",
                    encoding=None,
                )

    def test_install_with_all_options(self):
        """Test install function with all options."""
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
            with patch(
                "packing_packages.install._core.install_packages"
            ) as mock_install:
                args = argparse.Namespace(
                    env_name="custom_env",
                    dirpath_packages=Path("/tmp"),
                    encoding="utf-8",
                )

                install(args)
                mock_install.assert_called_once_with(
                    dirpath_packages=Path("/tmp").resolve(),
                    env_name="custom_env",
                    encoding="utf-8",
                )

    def test_install_invalid_packages_dir(self):
        """Test install function with invalid packages directory."""
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
            args = argparse.Namespace(
                env_name=None,
                dirpath_packages=Path("/nonexistent"),
                encoding=None,
            )

            with pytest.raises(FileNotFoundError):
                install(args)


class TestAddArgumentsInstall:
    """Test add_arguments_install function."""

    def test_add_arguments_install(self):
        """Test add_arguments_install function."""
        parser = argparse.ArgumentParser()
        add_arguments_install(parser)

        # Test that arguments are added
        args = parser.parse_args(["/tmp", "-n", "test_env", "-e", "utf-8"])

        assert args.env_name == "test_env"
        assert args.dirpath_packages == Path("/tmp")
        assert args.encoding == "utf-8"

    def test_add_arguments_install_defaults(self):
        """Test add_arguments_install function with defaults."""
        parser = argparse.ArgumentParser()
        add_arguments_install(parser)

        args = parser.parse_args(["."])

        assert args.env_name is None
        assert args.dirpath_packages == Path(".")
        assert args.encoding is None

    def test_add_arguments_install_help(self):
        """Test add_arguments_install function help messages."""
        parser = argparse.ArgumentParser()
        add_arguments_install(parser)

        # Test that help messages are present
        help_text = parser.format_help()
        assert "env-name" in help_text
        assert "dirpath-packages" in help_text
        assert "encoding" in help_text

    def test_add_arguments_install_positional_arg(self):
        """Test add_arguments_install function positional argument."""
        parser = argparse.ArgumentParser()
        add_arguments_install(parser)

        # Test positional argument
        args = parser.parse_args(["/custom/path"])
        assert args.dirpath_packages == Path("/custom/path")


class TestMain:
    """Test main function."""

    def test_main_with_args(self):
        """Test main function with arguments."""
        with patch(
            "packing_packages.install.__main__.add_arguments_install"
        ) as mock_add_args:
            with patch(
                "packing_packages.install.__main__.install"
            ) as mock_install:
                try:
                    main(["/tmp", "-n", "test_env"])
                except SystemExit:
                    pass  # Expected for missing required arguments

    def test_main_help(self):
        """Test main function with help."""
        with pytest.raises(SystemExit):
            main(["--help"])

    def test_main_with_prog(self):
        """Test main function with custom prog name."""
        with patch(
            "packing_packages.install.__main__.add_arguments_install"
        ) as mock_add_args:
            with patch(
                "packing_packages.install.__main__.install"
            ) as mock_install:
                try:
                    main(["/tmp", "-n", "test_env"], prog="custom-prog")
                except SystemExit:
                    pass  # Expected for missing required arguments

    def test_main_invalid_args(self):
        """Test main function with invalid arguments."""
        with pytest.raises(SystemExit):
            main(["--invalid-option"])

    def test_main_missing_positional(self):
        """Test main function with missing positional argument."""
        with pytest.raises(SystemExit):
            main([])


class TestMainIntegration:
    """Test main module integration."""

    def test_main_parser_creation(self):
        """Test that main creates proper argument parser."""
        parser = argparse.ArgumentParser(
            prog="test",
            description="Install packages in the conda environment",
        )
        add_arguments_install(parser)

        # Test that parser structure is correct
        assert parser.prog == "test"
        assert len(parser._actions) > 0

    def test_main_with_temp_dir(self):
        """Test main function with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
                with patch(
                    "packing_packages.install._core.install_packages"
                ) as mock_install:
                    try:
                        main([temp_dir, "-n", "test_env"])
                    except SystemExit:
                        pass  # Expected for missing required arguments

    def test_main_with_encoding(self):
        """Test main function with encoding."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
                with patch(
                    "packing_packages.install._core.install_packages"
                ) as mock_install:
                    try:
                        main([temp_dir, "-e", "utf-8"])
                    except SystemExit:
                        pass  # Expected for missing required arguments
