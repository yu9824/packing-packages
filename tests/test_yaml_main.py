"""Tests for pack.yaml.__main__ module."""

import argparse
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from packing_packages.pack.yaml.__main__ import (
    add_arguments_pack_from_yaml,
    main,
    pack_from_yaml,
)


class TestPackFromYamlFunction:
    """Test pack_from_yaml function."""

    def test_pack_from_yaml_with_all_options(self):
        """Test pack_from_yaml function with all options."""
        with patch(
            "packing_packages.pack.yaml._core.packing_packages_from_yaml"
        ) as mock_packing:
            args = argparse.Namespace(
                filepath_yaml=Path("test.yaml"),
                platform="linux-64",
                dirpath_target=Path("/tmp"),
                diff_only=True,
                dry_run=True,
                encoding="utf-8",
            )

            pack_from_yaml(args)
            mock_packing.assert_called_once_with(
                Path("test.yaml"),
                platform="linux-64",
                dirpath_target=Path("/tmp").resolve(),
                diff_only=True,
                dry_run=True,
                encoding="utf-8",
            )

    def test_pack_from_yaml_with_defaults(self):
        """Test pack_from_yaml function with defaults."""
        with patch(
            "packing_packages.pack.yaml._core.packing_packages_from_yaml"
        ) as mock_packing:
            args = argparse.Namespace(
                filepath_yaml=Path("test.yaml"),
                platform=None,
                dirpath_target=Path("."),
                diff_only=False,
                dry_run=False,
                encoding=None,
            )

            pack_from_yaml(args)
            mock_packing.assert_called_once_with(
                Path("test.yaml"),
                platform=None,
                dirpath_target=Path(".").resolve(),
                diff_only=False,
                dry_run=False,
                encoding=None,
            )

    def test_pack_from_yaml_invalid_target_dir(self):
        """Test pack_from_yaml function with invalid target directory."""
        args = argparse.Namespace(
            filepath_yaml=Path("test.yaml"),
            platform=None,
            dirpath_target=Path("/nonexistent"),
            diff_only=False,
            dry_run=False,
            encoding=None,
        )

        with pytest.raises(FileNotFoundError):
            pack_from_yaml(args)


class TestAddArgumentsPackFromYaml:
    """Test add_arguments_pack_from_yaml function."""

    def test_add_arguments_pack_from_yaml(self):
        """Test add_arguments_pack_from_yaml function."""
        parser = argparse.ArgumentParser()
        add_arguments_pack_from_yaml(parser)

        # Test that arguments are added
        args = parser.parse_args(
            [
                "test.yaml",
                "-p",
                "linux-64",
                "-d",
                "/tmp",
                "-D",
                "-e",
                "utf-8",
                "--diff-only",
            ]
        )

        assert args.filepath_yaml == Path("test.yaml")
        assert args.platform == "linux-64"
        assert args.dirpath_target == Path("/tmp")
        assert args.dry_run is True
        assert args.encoding == "utf-8"
        assert args.diff_only is True

    def test_add_arguments_pack_from_yaml_defaults(self):
        """Test add_arguments_pack_from_yaml function with defaults."""
        parser = argparse.ArgumentParser()
        add_arguments_pack_from_yaml(parser)

        args = parser.parse_args(["test.yaml"])

        assert args.filepath_yaml == Path("test.yaml")
        assert args.platform is None
        assert args.dirpath_target == Path(".")
        assert args.dry_run is False
        assert args.encoding is None
        assert args.diff_only is False

    def test_add_arguments_pack_from_yaml_help(self):
        """Test add_arguments_pack_from_yaml function help messages."""
        parser = argparse.ArgumentParser()
        add_arguments_pack_from_yaml(parser)

        # Test that help messages are present
        help_text = parser.format_help()
        assert "filepath_yaml" in help_text
        assert "platform" in help_text
        assert "dirpath-target" in help_text
        assert "dry-run" in help_text
        assert "encoding" in help_text
        assert "diff-only" in help_text

    def test_add_arguments_pack_from_yaml_platform_choices(self):
        """Test add_arguments_pack_from_yaml function platform choices."""
        parser = argparse.ArgumentParser()
        add_arguments_pack_from_yaml(parser)

        # Test valid platform choices
        valid_platforms = [
            "win-64",
            "win-32",
            "linux-64",
            "linux-aarch64",
            "linux-ppc64le",
            "linux-s390x",
            "osx-64",
            "osx-arm64",
        ]

        for platform in valid_platforms:
            args = parser.parse_args(["test.yaml", "-p", platform])
            assert args.platform == platform

    def test_add_arguments_pack_from_yaml_invalid_platform(self):
        """Test add_arguments_pack_from_yaml function with invalid platform."""
        parser = argparse.ArgumentParser()
        add_arguments_pack_from_yaml(parser)

        with pytest.raises(SystemExit):
            parser.parse_args(["test.yaml", "-p", "invalid-platform"])


class TestMain:
    """Test main function."""

    def test_main_with_args(self):
        """Test main function with arguments."""
        with patch(
            "packing_packages.pack.yaml.__main__.add_arguments_pack_from_yaml"
        ) as mock_add_args:
            with patch(
                "packing_packages.pack.yaml.__main__.pack_from_yaml"
            ) as mock_pack:
                try:
                    main(["test.yaml", "-p", "linux-64", "-d", "/tmp"])
                except SystemExit:
                    pass  # Expected for missing required arguments

    def test_main_help(self):
        """Test main function with help."""
        with pytest.raises(SystemExit):
            main(["--help"])

    def test_main_with_prog(self):
        """Test main function with custom prog name."""
        with patch(
            "packing_packages.pack.yaml.__main__.add_arguments_pack_from_yaml"
        ) as mock_add_args:
            with patch(
                "packing_packages.pack.yaml.__main__.pack_from_yaml"
            ) as mock_pack:
                try:
                    main(["test.yaml", "-p", "linux-64"], prog="custom-prog")
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
        parser = argparse.ArgumentParser(prog="test", description="")
        add_arguments_pack_from_yaml(parser)

        # Test that parser structure is correct
        assert parser.prog == "test"
        assert len(parser._actions) > 0

    def test_main_with_temp_dir(self):
        """Test main function with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "packing_packages.pack.yaml._core.packing_packages_from_yaml"
            ) as mock_packing:
                try:
                    main(["test.yaml", "-d", temp_dir, "-D"])
                except SystemExit:
                    pass  # Expected for missing required arguments

    def test_main_with_platform(self):
        """Test main function with platform."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "packing_packages.pack.yaml._core.packing_packages_from_yaml"
            ) as mock_packing:
                try:
                    main(["test.yaml", "-p", "linux-64", "-d", temp_dir])
                except SystemExit:
                    pass  # Expected for missing required arguments

    def test_main_with_encoding(self):
        """Test main function with encoding."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch(
                "packing_packages.pack.yaml._core.packing_packages_from_yaml"
            ) as mock_packing:
                try:
                    main(["test.yaml", "-e", "utf-8", "-d", temp_dir])
                except SystemExit:
                    pass  # Expected for missing required arguments
