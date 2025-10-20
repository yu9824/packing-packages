"""Tests for pack._core module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from packing_packages.pack._core import (
    Package,
    get_existing_packages_conda,
    get_existing_packages_pypi,
    packing_packages,
)


class TestPackage:
    """Test Package NamedTuple."""

    def test_package_creation(self):
        """Test Package creation."""
        package = Package(
            name="test-package",
            version="1.0.0",
            build="build123",
            channel="conda-forge",
        )

        assert package.name == "test-package"
        assert package.version == "1.0.0"
        assert package.build == "build123"
        assert package.channel == "conda-forge"

    def test_package_slicing(self):
        """Test Package slicing."""
        package = Package("test", "1.0.0", "build", "channel")
        assert package[:3] == ("test", "1.0.0", "build")
        assert package[:2] == ("test", "1.0.0")


class TestGetExistingPackagesConda:
    """Test get_existing_packages_conda function."""

    def test_get_existing_packages_conda_empty_dir(self):
        """Test get_existing_packages_conda with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_existing_packages_conda(temp_dir)
            assert result == set()

    def test_get_existing_packages_conda_with_files(self):
        """Test get_existing_packages_conda with conda package files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test conda package files
            (temp_path / "test-package-1.0.0-build123.tar.bz2").touch()
            (temp_path / "another-package-2.0.0-build456.conda").touch()
            (temp_path / "invalid-name.txt").touch()  # Should be ignored

            result = get_existing_packages_conda(temp_dir)

            expected = {
                ("test-package", "1.0.0", "build123"),
                ("another-package", "2.0.0", "build456"),
            }
            assert result == expected

    def test_get_existing_packages_conda_nested_dirs(self):
        """Test get_existing_packages_conda with nested directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nested_dir = temp_path / "nested"
            nested_dir.mkdir()

            (nested_dir / "nested-package-1.0.0-build.tar.bz2").touch()

            result = get_existing_packages_conda(temp_dir)

            expected = {("nested-package", "1.0.0", "build")}
            assert result == expected


class TestGetExistingPackagesPypi:
    """Test get_existing_packages_pypi function."""

    def test_get_existing_packages_pypi_empty_dir(self):
        """Test get_existing_packages_pypi with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_existing_packages_pypi(temp_dir)
            assert result == set()

    def test_get_existing_packages_pypi_with_files(self):
        """Test get_existing_packages_pypi with PyPI package files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test PyPI package files
            (temp_path / "test_package-1.0.0-py3-none-any.whl").touch()
            (temp_path / "another-package-2.0.0.tar.gz").touch()
            (temp_path / "invalid-name.txt").touch()  # Should be ignored

            result = get_existing_packages_pypi(temp_dir)

            expected = {
                ("test_package", "1.0.0"),
                ("test-package", "1.0.0"),  # underscore to hyphen conversion
                ("another-package", "2.0.0"),
            }
            assert result == expected

    def test_get_existing_packages_pypi_nested_dirs(self):
        """Test get_existing_packages_pypi with nested directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            nested_dir = temp_path / "nested"
            nested_dir.mkdir()

            (nested_dir / "nested_package-1.0.0-py3-none-any.whl").touch()

            result = get_existing_packages_pypi(temp_dir)

            expected = {
                ("nested_package", "1.0.0"),
                ("nested-package", "1.0.0"),
            }
            assert result == expected


class TestPackingPackages:
    """Test packing_packages function."""

    def test_packing_packages_no_conda_exe(self):
        """Test packing_packages without CONDA_EXE environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Please install conda"):
                packing_packages()

    def test_packing_packages_invalid_env_name(self):
        """Test packing_packages with invalid environment name."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with patch("subprocess.run") as mock_run:
                # Mock conda info -e to return empty environment list
                mock_run.return_value.stdout = b"# environments:\n"
                mock_run.return_value.returncode = 0

                with pytest.raises(ValueError, match="is not found"):
                    packing_packages(env_name="nonexistent_env")

    def test_packing_packages_invalid_target_dir(self):
        """Test packing_packages with invalid target directory."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with pytest.raises(FileNotFoundError):
                packing_packages(dirpath_target="/nonexistent/dir")

    def test_packing_packages_dry_run(self):
        """Test packing_packages in dry run mode."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with patch("subprocess.run") as mock_run:
                # Mock conda list output
                mock_run.return_value.stdout = (
                    b"# packages in environment\npython 3.9.0 py39_0\n"
                )
                mock_run.return_value.returncode = 0

                with tempfile.TemporaryDirectory() as temp_dir:
                    # Should not raise exception in dry run mode
                    packing_packages(dirpath_target=temp_dir, dry_run=True)

    @patch("packing_packages.pack._core.tqdm")
    def test_packing_packages_with_packages(self, mock_tqdm):
        """Test packing_packages with actual packages."""
        mock_tqdm.return_value = [Package("python", "3.9.0", "py39_0", "")]

        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with patch("subprocess.run") as mock_run:
                # Mock conda list output
                mock_run.return_value.stdout = (
                    b"# packages in environment\npython 3.9.0 py39_0\n"
                )
                mock_run.return_value.returncode = 0

                with tempfile.TemporaryDirectory() as temp_dir:
                    with patch("packing_packages.pack._core.copyfile"):
                        # Should not raise exception
                        packing_packages(dirpath_target=temp_dir, dry_run=True)

    def test_packing_packages_diff_only_existing_dir(self):
        """Test packing_packages with diff_only and existing directory."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.stdout = (
                    b"# packages in environment\npython 3.9.0 py39_0\n"
                )
                mock_run.return_value.returncode = 0

                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    env_dir = temp_path / "test"
                    env_dir.mkdir()

                    # Create some existing packages
                    (env_dir / "conda").mkdir()
                    (env_dir / "pypi").mkdir()

                    with patch(
                        "packing_packages.pack._core.get_existing_packages_conda",
                        return_value=set(),
                    ):
                        with patch(
                            "packing_packages.pack._core.get_existing_packages_pypi",
                            return_value=set(),
                        ):
                            with patch("packing_packages.pack._core.copyfile"):
                                # Should not raise exception
                                packing_packages(
                                    dirpath_target=temp_dir,
                                    diff_only=True,
                                    dry_run=True,
                                )

    def test_packing_packages_python_version_warning(self):
        """Test packing_packages with Python version mismatch warning."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with patch("subprocess.run") as mock_run:
                # Mock conda list output with different Python version
                mock_run.return_value.stdout = (
                    b"# packages in environment\npython 2.7.0 py27_0\n"
                )
                mock_run.return_value.returncode = 0

                with tempfile.TemporaryDirectory() as temp_dir:
                    with patch(
                        "packing_packages.pack._core._logger"
                    ) as mock_logger:
                        packing_packages(dirpath_target=temp_dir, dry_run=True)
                        # Should log warning about Python version mismatch
                        mock_logger.warning.assert_called()
