"""Utility functions for packing packages.

This module contains common utility functions used by both pack._core and pack.yaml._core.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from shutil import copyfile

from packing_packages.constants import EXTENSIONS_CONDA
from packing_packages.logging import get_child_logger

from ._types import (
    Package,
    get_existing_packages_conda,
    get_existing_packages_pypi,
)

_logger = get_child_logger(__name__)


def check_conda_installation() -> Path:
    """Check conda installation and return conda package directory path.

    Returns
    -------
    Path
        Path to conda package cache directory.

    Raises
    ------
    ValueError
        If conda is not installed or CONDA_EXE environment variable is not set.
    """
    if "CONDA_EXE" not in os.environ:
        raise ValueError(
            "Please install conda and set the CONDA_EXE environment variable."
        )
    DIRPATH_CONDA_ROOT = Path(os.environ["CONDA_EXE"]).parent.parent.resolve()
    return DIRPATH_CONDA_ROOT / "pkgs"


def prepare_output_directory(
    dirpath_target: Path,
    env_name: str,
    diff_only: bool,
    dry_run: bool,
) -> tuple[Path, set[tuple[str, str, str]], set[tuple[str, str]]]:
    """Prepare output directory and get existing packages if diff_only is True.

    Parameters
    ----------
    dirpath_target : Path
        Target directory path.
    env_name : str
        Environment name.
    diff_only : bool
        If True, only download packages that are not already downloaded.
    dry_run : bool
        If True, do not create directories.

    Returns
    -------
    tuple[Path, set[tuple[str, str, str]], set[tuple[str, str]]]
        Tuple of (output directory path, existing conda packages set, existing pypi packages set).
    """
    dirpath_target = dirpath_target.resolve()
    if not dirpath_target.is_dir():
        raise FileNotFoundError(dirpath_target)

    dirpath_output = dirpath_target / env_name
    if dirpath_output.is_dir():
        if diff_only:
            _logger.info(
                f"Output directory '{dirpath_output}' already exists. "
                "Only downloading missing packages..."
            )

            st_existing_conda = get_existing_packages_conda(dirpath_output)
            st_existing_pypi = get_existing_packages_pypi(dirpath_output)

            # Update dirpath_output to diff directory
            dirpath_output = (
                dirpath_output
                / "diffs"
                / datetime.now().strftime("%Y%m%d_%H%M")
            )
            dirpath_output.mkdir(parents=True)
        else:
            _logger.warning(
                f"Output directory '{dirpath_output}' already exists. "
                "We will add files to this directory. "
                "If you want to add only missing packages, set 'diff_only=True'."
            )

            st_existing_conda = set()
            st_existing_pypi = set()
    else:
        st_existing_conda = set()
        st_existing_pypi = set()

    if not dry_run:
        os.makedirs(dirpath_output, exist_ok=True)

    _logger.info(f"Packing to '{dirpath_output}'...")

    dirpath_output_pypi = dirpath_output / "pypi"
    dirpath_output_conda = dirpath_output / "conda"
    for _dirpath in (dirpath_output_pypi, dirpath_output_conda):
        if not dry_run:
            os.makedirs(_dirpath, exist_ok=True)

    return dirpath_output, st_existing_conda, st_existing_pypi


def check_python_version(env_python_version: str) -> None:
    """Check if the Python version of the environment matches the current Python version.

    Parameters
    ----------
    env_python_version : str
        Python version from the environment.
    """
    if (
        tuple(map(int, env_python_version.split(".")[:2]))
        != sys.version_info[:2]
    ):
        _logger.warning(
            "The Python version of the conda environment and the current Python version do not match. "
            "It is recommended to use the same Python version."
        )


def _is_valid_url(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status == 200:
                return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        pass

    return False


def _resolve_pypi_requirement(package: Package) -> tuple[str, str | None]:
    """Resolve the pip requirement string and index URL for a package.

    For PyTorch packages with a local version label (e.g. ``2.1.0+cu118``),
    use the PyTorch index (``https://download.pytorch.org/whl/cu118``) if it
    is reachable. Otherwise, keep the original version so that pip fails
    explicitly.

    Parameters
    ----------
    package : Package
        Package to resolve.

    Returns
    -------
    tuple[str, str | None]
        Requirement string (e.g. ``torch==2.1.0``) and index URL
        (None means the default index).
    """
    if package.name.startswith("torch") and "+" in package.version:
        version, _, device = package.version.partition("+")
        index_url_torch = f"https://download.pytorch.org/whl/{device}"
        if _is_valid_url(index_url_torch):
            return f"{package.name}=={version}", index_url_torch

    return f"{package.name}=={package.version}", None


def _build_pip_command(
    requirement: str,
    dirpath_output_pypi: Path,
    env_python_version: str,
    dry_run: bool,
    platform_pypi: str | None,
    index_url: str | None,
) -> list[str]:
    """Build the pip command to download (or dry-run install) a package.

    Parameters
    ----------
    requirement : str
        Requirement string (e.g. ``numpy==1.26.0``).
    dirpath_output_pypi : Path
        Output directory for PyPI packages.
    env_python_version : str
        Python version for the package.
    dry_run : bool
        If True, use ``pip install --dry-run`` instead of ``pip download``.
    platform_pypi : str, optional
        Platform specification for PyPI package.
    index_url : str, optional
        Base URL of the package index. If None, use the default index.

    Returns
    -------
    list[str]
        pip command.
    """
    dirpath_output = str(dirpath_output_pypi)
    if dry_run:
        subcommand = "install"
        mode_args = ["--no-build-isolation", "--dry-run", "--force-reinstall"]
        # For compatibility with original pack._core.py implementation
        output_args = [] if platform_pypi else ["--target", dirpath_output]
    else:
        subcommand = "download"
        mode_args = []
        output_args = ["-d", dirpath_output]

    platform_args = ["--platform", platform_pypi] if platform_pypi else []
    index_url_args = ["--index-url", index_url] if index_url else []

    return [
        sys.executable,
        "-m",
        "pip",
        subcommand,
        requirement,
        "--no-deps",
        "--python-version",
        env_python_version,
        *mode_args,
        *output_args,
        *platform_args,
        *index_url_args,
    ]


def download_pypi_package(
    package: Package,
    dirpath_output_pypi: Path,
    env_python_version: str,
    encoding: str,
    dry_run: bool,
    platform_pypi: str | None = None,
) -> bool:
    """Download a PyPI package.

    Parameters
    ----------
    package : Package
        Package to download.
    dirpath_output_pypi : Path
        Output directory for PyPI packages.
    env_python_version : str
        Python version for the package.
    encoding : str
        Encoding for subprocess output.
    dry_run : bool
        If True, do not download files.
    platform_pypi : str, optional
        Platform specification for PyPI package.

    Returns
    -------
    bool
        True if download succeeded, False otherwise.
    """
    requirement, index_url = _resolve_pypi_requirement(package)

    cmd = _build_pip_command(
        requirement=requirement,
        dirpath_output_pypi=dirpath_output_pypi,
        env_python_version=env_python_version,
        dry_run=dry_run,
        platform_pypi=platform_pypi,
        index_url=index_url,
    )

    result_pip_download = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    _logger.info("\n" + result_pip_download.stdout.decode(encoding))
    if result_pip_download.returncode != 0:
        _logger.warning(f"'{package}' is not found.")
        _logger.error(result_pip_download.stderr.decode(encoding))
        return False
    return True


def download_conda_package(
    package: Package,
    dirpath_pkgs: Path,
    dirpath_output_conda: Path,
    encoding: str,
    dry_run: bool,
    platform_conda: str | None = None,
    channels: list[str] | None = None,
) -> bool:
    """Download a conda package.

    Parameters
    ----------
    package : Package
        Package to download.
    dirpath_pkgs : Path
        Conda package cache directory.
    dirpath_output_conda : Path
        Output directory for conda packages.
    encoding : str
        Encoding for subprocess output.
    dry_run : bool
        If True, do not download files.
    platform_conda : str, optional
        Platform specification for conda package.
    channels : list[str], optional
        List of conda channels to use. If None, uses package.channel or defaults.

    Returns
    -------
    bool
        True if download succeeded, False otherwise.
    """
    tup_filepaths_package = tuple(
        dirpath_pkgs
        / f"{package.name}-{package.version}-{package.build}.{ext}"
        for ext in EXTENSIONS_CONDA
    )

    # あるときは、dirpath_pkgsからコピーする
    for filepath_package in tup_filepaths_package:
        if filepath_package.is_file():
            _logger.info(f"Copying '{filepath_package.name}' from cache...")
            if not dry_run:
                copyfile(
                    filepath_package,
                    dirpath_output_conda / filepath_package.name,
                )
            return True

    # ない場合は、直接ダウンロード
    _logger.info(f"{package} is not found in the conda package cache.")

    cmd = [
        os.environ["CONDA_EXE"],
        "search",
        f"{package.name}={package.version}={package.build}",
        "--info",
    ]
    if platform_conda:
        cmd.extend(["--platform", platform_conda])
    if channels:
        for channel in channels:
            cmd.extend(["-c", channel])
    elif package.channel:
        cmd.extend(["-c", package.channel])
    else:
        cmd.extend(["-c", "defaults"])

    result_conda_search = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if match_conda_package_url := re.search(
        r"url\s*:\s*(https?://\S+\.{})".format(
            r"(?:" + r"|".join(EXTENSIONS_CONDA).replace(r".", r"\.") + r")"
        ),
        result_conda_search.stdout.decode(encoding),
    ):
        url = match_conda_package_url.group(1)
    else:
        _logger.warning("Could not detect the URL of the conda package.")
        return False

    filename_download_conda = Path(url).name
    _logger.info(f"Downloading '{filename_download_conda}' from {url}")
    if not dry_run:
        try:
            _ = urllib.request.urlretrieve(
                url, dirpath_output_conda / filename_download_conda
            )
        except Exception as error:
            _logger.exception(repr(error))
            _logger.warning(
                f"'{filename_download_conda}' could not be downloaded from {url}."
            )
            return False
    return True


def log_packing_results(
    list_packages: list[Package],
    list_failed_packages: list[Package],
) -> tuple[int, int]:
    """Log packing results.

    Parameters
    ----------
    list_packages : list[Package]
        List of all packages.
    list_failed_packages : list[Package]
        List of failed packages.

    Returns
    -------
    tuple[int, int]
        Tuple of (number of successful packages, number of failed packages).
    """
    n_success = len(list_packages) - len(list_failed_packages)
    n_failed = len(list_failed_packages)
    _logger.info(
        f"{n_success} / {(n_success + n_failed)} packages are success!"
    )

    if n_failed > 0:
        for package in list_failed_packages:
            _logger.warning(f"  {package.name}=={package.version}")
        _logger.warning(
            "Please check the above packages. "
            "You can try to download them manually."
        )
    return n_success, n_failed
