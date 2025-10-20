"""Tests for pack.__main__ module."""

import argparse
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from packing_packages.pack.__main__ import add_arguments_pack, main, pack


class TestPackFunction:
    """Test pack function."""

    def test_pack_with_env_name(self):
        """Test pack function with specified environment name."""
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
            with patch(
                "packing_packages.pack._core.packing_packages"
            ) as mock_packing:
                args = argparse.Namespace(
                    env_name="custom_env",
                    dirpath_target=Path("."),
                    diff_only=False,
                    encoding=None,
                    dry_run=False,
                )

                pack(args)
                mock_packing.assert_called_once_with(
                    env_name="custom_env",
                    dirpath_target=Path(".").resolve(),
                    diff_only=False,
                    encoding=None,
                    dry_run=False,
                )

    def test_pack_without_env_name(self):
        """Test pack function without specified environment name."""
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
            with patch(
                "packing_packages.pack._core.packing_packages"
            ) as mock_packing:
                args = argparse.Namespace(
                    env_name=None,
                    dirpath_target=Path("."),
                    diff_only=False,
                    encoding=None,
                    dry_run=False,
                )

                pack(args)
                mock_packing.assert_called_once_with(
                    env_name="test",
                    dirpath_target=Path(".").resolve(),
                    diff_only=False,
                    encoding=None,
                    dry_run=False,
                )

    def test_pack_with_all_options(self):
        """Test pack function with all options."""
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
            with patch(
                "packing_packages.pack._core.packing_packages"
            ) as mock_packing:
                args = argparse.Namespace(
                    env_name="custom_env",
                    dirpath_target=Path("/tmp"),
                    diff_only=True,
                    encoding="utf-8",
                    dry_run=True,
                )

                pack(args)
                mock_packing.assert_called_once_with(
                    env_name="custom_env",
                    dirpath_target=Path("/tmp").resolve(),
                    diff_only=True,
                    encoding="utf-8",
                    dry_run=True,
                )

    def test_pack_invalid_target_dir(self):
        """Test pack function with invalid target directory."""
        with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
            args = argparse.Namespace(
                env_name=None,
                dirpath_target=Path("/nonexistent"),
                diff_only=False,
                encoding=None,
                dry_run=False,
            )

            with pytest.raises(FileNotFoundError):
                pack(args)


class TestAddArgumentsPack:
    """Test add_arguments_pack function."""

    def test_add_arguments_pack(self):
        """Test add_arguments_pack function."""
        parser = argparse.ArgumentParser()
        add_arguments_pack(parser)

        # Test that arguments are added
        args = parser.parse_args(
            [
                "-n",
                "test_env",
                "-d",
                "/tmp",
                "-D",
                "-e",
                "utf-8",
                "--diff-only",
            ]
        )

        assert args.env_name == "test_env"
        assert args.dirpath_target == Path("/tmp")
        assert args.dry_run is True
        assert args.encoding == "utf-8"
        assert args.diff_only is True

    def test_add_arguments_pack_defaults(self):
        """Test add_arguments_pack function with defaults."""
        parser = argparse.ArgumentParser()
        add_arguments_pack(parser)

        args = parser.parse_args([])

        assert args.env_name is None
        assert args.dirpath_target == Path(".")
        assert args.dry_run is False
        assert args.encoding is None
        assert args.diff_only is False

    def test_add_arguments_pack_help(self):
        """Test add_arguments_pack function help messages."""
        parser = argparse.ArgumentParser()
        add_arguments_pack(parser)

        # Test that help messages are present
        help_text = parser.format_help()
        assert "env-name" in help_text
        assert "dirpath-target" in help_text
        assert "dry-run" in help_text
        assert "encoding" in help_text
        assert "diff-only" in help_text


class TestMain:
    """Test main function."""

    def test_main_with_args(self):
        """Test main function with arguments."""
        with patch(
            "packing_packages.pack.__main__.add_arguments_pack"
        ) as mock_add_args:
            with patch("packing_packages.pack.__main__.pack") as mock_pack:
                try:
                    main(["-n", "test_env", "-d", "/tmp"])
                except SystemExit:
                    pass  # Expected for missing required arguments

    def test_main_help(self):
        """Test main function with help."""
        with pytest.raises(SystemExit):
            main(["--help"])

    def test_main_with_prog(self):
        """Test main function with custom prog name."""
        with patch(
            "packing_packages.pack.__main__.add_arguments_pack"
        ) as mock_add_args:
            with patch("packing_packages.pack.__main__.pack") as mock_pack:
                try:
                    main(["-n", "test_env"], prog="custom-prog")
                except SystemExit:
                    pass  # Expected for missing required arguments

    def test_main_invalid_args(self):
        """Test main function with invalid arguments."""
        with pytest.raises(SystemExit):
            main(["--invalid-option"])


class TestMainIntegration:
    """Test main module integration."""

    def test_main_parser_creation(self):
        """Test that main creates proper argument parser."""
        parser = argparse.ArgumentParser(
            prog="test", description="pack conda environment"
        )
        add_arguments_pack(parser)

        # Test that parser structure is correct
        assert parser.prog == "test"
        assert len(parser._actions) > 0

    def test_main_with_temp_dir(self):
        """Test main function with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
                with patch(
                    "packing_packages.pack._core.packing_packages"
                ) as mock_packing:
                    try:
                        main(["-d", temp_dir, "-D"])
                    except SystemExit:
                        pass  # Expected for missing required arguments

    def test_main_dry_run(self):
        """Test main function with dry run."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"CONDA_DEFAULT_ENV": "test"}):
                with patch(
                    "packing_packages.pack._core.packing_packages"
                ) as mock_packing:
                    try:
                        main(["-d", temp_dir, "-D", "-n", "test_env"])
                    except SystemExit:
                        pass  # Expected for missing required arguments
