"""Tests for install._core module."""

import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from packing_packages.install._core import install_packages


class TestInstallPackages:
    """Test install_packages function."""

    def test_install_packages_no_conda_exe(self):
        """Test install_packages without CONDA_EXE environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Please install conda"):
                install_packages()

    def test_install_packages_invalid_env_name(self):
        """Test install_packages with invalid environment name."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with patch("subprocess.run") as mock_run:
                # Mock conda info -e to return empty environment list
                mock_run.return_value.stdout = b"# environments:\n"
                mock_run.return_value.returncode = 0

                with pytest.raises(
                    ValueError, match="Environment 'nonexistent_env' not found"
                ):
                    install_packages(env_name="nonexistent_env")

    def test_install_packages_invalid_packages_dir(self):
        """Test install_packages with invalid packages directory."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with pytest.raises(FileNotFoundError):
                install_packages(dirpath_packages="/nonexistent/dir")

    def test_install_packages_empty_directory(self):
        """Test install_packages with empty directory."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                with patch("packing_packages.install._core.tqdm") as mock_tqdm:
                    mock_tqdm.return_value = []

                    # Should not raise exception with empty directory
                    install_packages(dirpath_packages=temp_dir)

    def test_install_packages_with_conda_packages(self):
        """Test install_packages with conda packages."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create test conda package files
                (temp_path / "test-package-1.0.0-build.tar.bz2").touch()
                (temp_path / "another-package-2.0.0-build.conda").touch()

                with patch("packing_packages.install._core.tqdm") as mock_tqdm:
                    mock_tqdm.return_value = [
                        temp_path / "test-package-1.0.0-build.tar.bz2",
                        temp_path / "another-package-2.0.0-build.conda",
                    ]

                    with patch("subprocess.run") as mock_run:
                        mock_run.return_value.stdout = b"Success"
                        mock_run.return_value.stderr = b""
                        mock_run.return_value.returncode = 0

                        # Should not raise exception
                        install_packages(dirpath_packages=temp_dir)

    def test_install_packages_with_pypi_packages(self):
        """Test install_packages with PyPI packages."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create test PyPI package files
                (temp_path / "test_package-1.0.0-py3-none-any.whl").touch()
                (temp_path / "another-package-2.0.0.tar.gz").touch()

                with patch("packing_packages.install._core.tqdm") as mock_tqdm:
                    mock_tqdm.return_value = [
                        temp_path / "test_package-1.0.0-py3-none-any.whl",
                        temp_path / "another-package-2.0.0.tar.gz",
                    ]

                    with patch("subprocess.run") as mock_run:
                        mock_run.return_value.stdout = b"Success"
                        mock_run.return_value.stderr = b""
                        mock_run.return_value.returncode = 0

                        # Should not raise exception
                        install_packages(dirpath_packages=temp_dir)

    def test_install_packages_conda_install_failure(self):
        """Test install_packages with conda install failure."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create test conda package file
                test_file = temp_path / "test-package-1.0.0-build.tar.bz2"
                test_file.touch()

                with patch("packing_packages.install._core.tqdm") as mock_tqdm:
                    mock_tqdm.return_value = [test_file]

                    with patch("subprocess.run") as mock_run:
                        mock_run.return_value.stdout = b"Error"
                        mock_run.return_value.stderr = b"Installation failed"
                        mock_run.return_value.returncode = 1

                        with patch(
                            "packing_packages.install._core._logger"
                        ) as mock_logger:
                            # Should not raise exception, but log warnings
                            install_packages(dirpath_packages=temp_dir)

                            # Should log warnings about failed installation
                            mock_logger.warning.assert_called()
                            mock_logger.error.assert_called()

    def test_install_packages_pip_install_failure(self):
        """Test install_packages with pip install failure."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create test PyPI package file
                test_file = temp_path / "test_package-1.0.0-py3-none-any.whl"
                test_file.touch()

                with patch("packing_packages.install._core.tqdm") as mock_tqdm:
                    mock_tqdm.return_value = [test_file]

                    with patch("subprocess.run") as mock_run:
                        mock_run.return_value.stdout = b"Error"
                        mock_run.return_value.stderr = b"Installation failed"
                        mock_run.return_value.returncode = 1

                        with patch(
                            "packing_packages.install._core._logger"
                        ) as mock_logger:
                            # Should not raise exception, but log warnings
                            install_packages(dirpath_packages=temp_dir)

                            # Should log warnings about failed installation
                            mock_logger.warning.assert_called()
                            mock_logger.error.assert_called()

    def test_install_packages_mixed_success_failure(self):
        """Test install_packages with mixed success and failure."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create test files
                success_file = (
                    temp_path / "success-package-1.0.0-build.tar.bz2"
                )
                failure_file = (
                    temp_path / "failure-package-2.0.0-build.tar.bz2"
                )
                success_file.touch()
                failure_file.touch()

                with patch("packing_packages.install._core.tqdm") as mock_tqdm:
                    mock_tqdm.return_value = [success_file, failure_file]

                    def mock_run_side_effect(cmd, **kwargs):
                        result = MagicMock()
                        if "success-package" in str(cmd):
                            result.stdout = b"Success"
                            result.stderr = b""
                            result.returncode = 0
                        else:
                            result.stdout = b"Error"
                            result.stderr = b"Installation failed"
                            result.returncode = 1
                        return result

                    with patch(
                        "subprocess.run", side_effect=mock_run_side_effect
                    ):
                        with patch(
                            "packing_packages.install._core._logger"
                        ) as mock_logger:
                            # Should not raise exception
                            install_packages(dirpath_packages=temp_dir)

                            # Should log both success and failure messages
                            mock_logger.info.assert_called()
                            mock_logger.warning.assert_called()

    def test_install_packages_encoding_parameter(self):
        """Test install_packages with encoding parameter."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                with patch("packing_packages.install._core.tqdm") as mock_tqdm:
                    mock_tqdm.return_value = []

                    # Should not raise exception with custom encoding
                    install_packages(
                        dirpath_packages=temp_dir, encoding="utf-8"
                    )

    def test_install_packages_nested_directories(self):
        """Test install_packages with nested directories."""
        with patch.dict(
            os.environ,
            {"CONDA_EXE": "/fake/conda", "CONDA_DEFAULT_ENV": "test"},
        ):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Create nested directory structure
                nested_dir = temp_path / "nested"
                nested_dir.mkdir()

                # Create test files in nested directory
                (nested_dir / "nested-package-1.0.0-build.tar.bz2").touch()
                (nested_dir / "nested_package-2.0.0-py3-none-any.whl").touch()

                with patch("packing_packages.install._core.tqdm") as mock_tqdm:
                    mock_tqdm.return_value = [
                        nested_dir / "nested-package-1.0.0-build.tar.bz2",
                        nested_dir / "nested_package-2.0.0-py3-none-any.whl",
                    ]

                    with patch("subprocess.run") as mock_run:
                        mock_run.return_value.stdout = b"Success"
                        mock_run.return_value.stderr = b""
                        mock_run.return_value.returncode = 0

                        # Should not raise exception
                        install_packages(dirpath_packages=temp_dir)
