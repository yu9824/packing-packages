"""Tests for pack.yaml._core module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from packing_packages.pack.yaml._core import packing_packages_from_yaml


class TestPackingPackagesFromYaml:
    """Test packing_packages_from_yaml function."""

    def test_packing_packages_from_yaml_no_conda_exe(self):
        """Test packing_packages_from_yaml without CONDA_EXE environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Please install conda"):
                packing_packages_from_yaml("test.yaml")

    def test_packing_packages_from_yaml_file_not_found(self):
        """Test packing_packages_from_yaml with non-existent file."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with pytest.raises(FileNotFoundError):
                packing_packages_from_yaml("nonexistent.yaml")

    def test_packing_packages_from_yaml_invalid_target_dir(self):
        """Test packing_packages_from_yaml with invalid target directory."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("""
name: test-env
channels:
  - conda-forge
dependencies:
  - python=3.9
  - numpy=1.21.0
""")
                f.flush()

                try:
                    with pytest.raises(FileNotFoundError):
                        packing_packages_from_yaml(
                            f.name, dirpath_target="/nonexistent/dir"
                        )
                finally:
                    os.unlink(f.name)

    def test_packing_packages_from_yaml_dry_run(self):
        """Test packing_packages_from_yaml in dry run mode."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("""
name: test-env
channels:
  - conda-forge
dependencies:
  - python=3.9
  - numpy=1.21.0
""")
                f.flush()

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with patch(
                            "packing_packages.pack.yaml._core.tqdm"
                        ) as mock_tqdm:
                            mock_tqdm.return_value = []

                            # Should not raise exception in dry run mode
                            packing_packages_from_yaml(
                                f.name, dirpath_target=temp_dir, dry_run=True
                            )
                finally:
                    os.unlink(f.name)

    def test_packing_packages_from_yaml_with_platform(self):
        """Test packing_packages_from_yaml with platform specification."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("""
name: test-env
channels:
  - conda-forge
dependencies:
  - python=3.9
  - numpy=1.21.0
""")
                f.flush()

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with patch(
                            "packing_packages.pack.yaml._core.tqdm"
                        ) as mock_tqdm:
                            mock_tqdm.return_value = []

                            # Should not raise exception with platform
                            packing_packages_from_yaml(
                                f.name,
                                platform="linux-64",
                                dirpath_target=temp_dir,
                                dry_run=True,
                            )
                finally:
                    os.unlink(f.name)

    def test_packing_packages_from_yaml_with_pip_dependencies(self):
        """Test packing_packages_from_yaml with pip dependencies."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("""
name: test-env
channels:
  - conda-forge
dependencies:
  - python=3.9
  - numpy=1.21.0
  - pip:
    - requests==2.25.1
    - pandas==1.3.0
""")
                f.flush()

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with patch(
                            "packing_packages.pack.yaml._core.tqdm"
                        ) as mock_tqdm:
                            mock_tqdm.return_value = []

                            # Should not raise exception with pip dependencies
                            packing_packages_from_yaml(
                                f.name, dirpath_target=temp_dir, dry_run=True
                            )
                finally:
                    os.unlink(f.name)

    def test_packing_packages_from_yaml_diff_only(self):
        """Test packing_packages_from_yaml with diff_only option."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("""
name: test-env
channels:
  - conda-forge
dependencies:
  - python=3.9
  - numpy=1.21.0
""")
                f.flush()

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir)
                        env_dir = temp_path / "test-env"
                        env_dir.mkdir()

                        # Create some existing packages
                        (env_dir / "conda").mkdir()
                        (env_dir / "pypi").mkdir()

                        with patch(
                            "packing_packages.pack.yaml._core.get_existing_packages_conda",
                            return_value=set(),
                        ):
                            with patch(
                                "packing_packages.pack.yaml._core.get_existing_packages_pypi",
                                return_value=set(),
                            ):
                                with patch(
                                    "packing_packages.pack.yaml._core.tqdm"
                                ) as mock_tqdm:
                                    mock_tqdm.return_value = []

                                    # Should not raise exception with diff_only
                                    packing_packages_from_yaml(
                                        f.name,
                                        dirpath_target=temp_dir,
                                        diff_only=True,
                                        dry_run=True,
                                    )
                finally:
                    os.unlink(f.name)

    def test_packing_packages_from_yaml_encoding(self):
        """Test packing_packages_from_yaml with encoding parameter."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("""
name: test-env
channels:
  - conda-forge
dependencies:
  - python=3.9
  - numpy=1.21.0
""")
                f.flush()

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with patch(
                            "packing_packages.pack.yaml._core.tqdm"
                        ) as mock_tqdm:
                            mock_tqdm.return_value = []

                            # Should not raise exception with encoding
                            packing_packages_from_yaml(
                                f.name,
                                dirpath_target=temp_dir,
                                encoding="utf-8",
                                dry_run=True,
                            )
                finally:
                    os.unlink(f.name)

    def test_packing_packages_from_yaml_python_version_warning(self):
        """Test packing_packages_from_yaml with Python version mismatch warning."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("""
name: test-env
channels:
  - conda-forge
dependencies:
  - python=2.7
  - numpy=1.21.0
""")
                f.flush()

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with patch(
                            "packing_packages.pack.yaml._core.tqdm"
                        ) as mock_tqdm:
                            mock_tqdm.return_value = []

                            with patch(
                                "packing_packages.pack.yaml._core._logger"
                            ) as mock_logger:
                                # Should not raise exception but log warning
                                packing_packages_from_yaml(
                                    f.name,
                                    dirpath_target=temp_dir,
                                    dry_run=True,
                                )

                                # Should log warning about Python version mismatch
                                mock_logger.warning.assert_called()
                finally:
                    os.unlink(f.name)

    def test_packing_packages_from_yaml_missing_python(self):
        """Test packing_packages_from_yaml with missing Python dependency."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("""
name: test-env
channels:
  - conda-forge
dependencies:
  - numpy=1.21.0
""")
                f.flush()

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with patch(
                            "packing_packages.pack.yaml._core.tqdm"
                        ) as mock_tqdm:
                            mock_tqdm.return_value = []

                            with pytest.raises(
                                AssertionError, match="Python has not found"
                            ):
                                packing_packages_from_yaml(
                                    f.name,
                                    dirpath_target=temp_dir,
                                    dry_run=True,
                                )
                finally:
                    os.unlink(f.name)

    def test_packing_packages_from_yaml_invalid_dependency_format(self):
        """Test packing_packages_from_yaml with invalid dependency format."""
        with patch.dict(os.environ, {"CONDA_EXE": "/fake/conda"}):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("""
name: test-env
channels:
  - conda-forge
dependencies:
  - python=3.9
  - invalid_dependency_format
""")
                f.flush()

                try:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        with patch(
                            "packing_packages.pack.yaml._core.tqdm"
                        ) as mock_tqdm:
                            mock_tqdm.return_value = []

                            with pytest.raises(ValueError):
                                packing_packages_from_yaml(
                                    f.name,
                                    dirpath_target=temp_dir,
                                    dry_run=True,
                                )
                finally:
                    os.unlink(f.name)
