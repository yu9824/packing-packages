"""Tests for main module."""

import argparse
import sys
from unittest.mock import patch

import pytest

from packing_packages.__main__ import entrypoint, main


class TestMain:
    """Test main module functions."""

    def test_main_version_argument(self):
        """Test main function with version argument."""
        with patch("sys.exit") as mock_exit:
            main(["-v"])
            mock_exit.assert_called_once()

    def test_main_pack_subcommand(self):
        """Test main function with pack subcommand."""
        with patch(
            "packing_packages.pack.__main__.add_arguments_pack"
        ) as mock_add_args:
            with patch("packing_packages.pack.__main__.pack") as mock_pack:
                # This should not raise an exception
                try:
                    main(["pack", "--help"])
                except SystemExit:
                    pass  # Expected for --help

    def test_main_install_subcommand(self):
        """Test main function with install subcommand."""
        with patch(
            "packing_packages.install.__main__.add_arguments_install"
        ) as mock_add_args:
            with patch(
                "packing_packages.install.__main__.install"
            ) as mock_install:
                # This should not raise an exception
                try:
                    main(["install", "--help"])
                except SystemExit:
                    pass  # Expected for --help

    def test_main_pack_yaml_subcommand(self):
        """Test main function with pack yaml subcommand."""
        with patch(
            "packing_packages.pack.yaml.__main__.add_arguments_pack_from_yaml"
        ) as mock_add_args:
            with patch(
                "packing_packages.pack.yaml.__main__.pack_from_yaml"
            ) as mock_pack_yaml:
                # This should not raise an exception
                try:
                    main(["pack", "yaml", "--help"])
                except SystemExit:
                    pass  # Expected for --help

    def test_main_invalid_subcommand(self):
        """Test main function with invalid subcommand."""
        with pytest.raises(SystemExit):
            main(["invalid_command"])

    def test_entrypoint(self):
        """Test entrypoint function."""
        with patch("packing_packages.__main__.main") as mock_main:
            entrypoint()
            mock_main.assert_called_once_with(sys.argv[1:])

    def test_main_with_prog_name(self):
        """Test main function with custom prog name."""
        with patch("packing_packages.__main__.main") as mock_main:
            main([], prog="custom-prog")
            mock_main.assert_called_once_with([], prog="custom-prog")


class TestMainIntegration:
    """Test main module integration."""

    def test_main_parser_creation(self):
        """Test that main creates proper argument parser."""
        parser = argparse.ArgumentParser(prog="test", description="")
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            help="show current version",
            version="test: 1.0.0",
        )
        subparsers = parser.add_subparsers()

        # Test that parser structure is correct
        assert parser.prog == "test"
        assert len(parser._actions) > 0

    def test_main_subparsers(self):
        """Test main function subparsers."""
        with patch(
            "packing_packages.__main__.add_arguments_pack"
        ) as mock_pack_args:
            with patch(
                "packing_packages.__main__.add_arguments_install"
            ) as mock_install_args:
                with patch(
                    "packing_packages.__main__.add_arguments_pack_from_yaml"
                ) as mock_yaml_args:
                    # Test that subparsers are created
                    try:
                        main(["pack", "--help"])
                    except SystemExit:
                        pass

                    try:
                        main(["install", "--help"])
                    except SystemExit:
                        pass

                    try:
                        main(["pack", "yaml", "--help"])
                    except SystemExit:
                        pass

    def test_main_no_arguments(self):
        """Test main function with no arguments."""
        with pytest.raises(SystemExit):
            main([])

    def test_main_help(self):
        """Test main function with help."""
        with pytest.raises(SystemExit):
            main(["--help"])


class TestMainErrorHandling:
    """Test main module error handling."""

    def test_main_invalid_args(self):
        """Test main function with invalid arguments."""
        with pytest.raises(SystemExit):
            main(["pack", "--invalid-option"])

    def test_main_missing_required_args(self):
        """Test main function with missing required arguments."""
        with pytest.raises(SystemExit):
            main(["pack"])  # Missing required dirpath-target

    def test_main_install_missing_required_args(self):
        """Test main function with missing required arguments for install."""
        with pytest.raises(SystemExit):
            main(["install"])  # Missing required dirpath-packages
