from __future__ import annotations

import os
import subprocess
from pathlib import Path

from packing_packages.helpers import (
    check_encoding,
    check_env_name,
    get_conda_sorted_packages_path,
    get_pypi_sorted_packages_path,
    is_installed,
)
from packing_packages.logging import get_child_logger

if is_installed("tqdm"):
    from tqdm.auto import tqdm  # type: ignore
else:
    from packing_packages.helpers import (  # type: ignore[assignment]
        dummy_tqdm as tqdm,
    )


_logger = get_child_logger(__name__)


def install_packages(
    env_name: str | None = None,
    dirpath_packages: str | os.PathLike = ".",
    encoding: str | None = None,
) -> None:
    """Install conda and PyPI packages.

    This function installs conda packages and PyPI packages from the specified
    directory into the specified conda environment. Conda packages are installed
    first, with Python packages prioritized. Failed installations are logged.

    Parameters
    ----------
    env_name : str, optional
        Conda environment name. If None, uses the current conda environment, by default None
    dirpath_packages : str | os.PathLike, optional
        Directory path containing packages to install, by default "."
    encoding : str, optional
        Encoding for subprocess output. If None, uses system default encoding, by default None

    Returns
    -------
    None
        This function does not return a value. Installation results are logged.
    """
    encoding = check_encoding(encoding)
    env_name = check_env_name(env_name, encoding)

    _logger.info(
        f"Installing packages from '{dirpath_packages}' into '{env_name}'"
    )

    dirpath_packages = Path(dirpath_packages).resolve()

    tup_filepaths_conda = get_conda_sorted_packages_path(dirpath_packages)
    tup_filepaths_pypi = get_pypi_sorted_packages_path(dirpath_packages)

    list_filepaths_conda_failed: list[Path] = []
    # install conda packages
    for filepath_conda in tqdm(
        tup_filepaths_conda,
        desc="Installing conda packages",
        unit="package",
    ):
        result_conda_install = subprocess.run(
            [
                os.environ["CONDA_EXE"],
                "install",
                "-y",
                "-n",
                env_name,
                "--offline",
                "--use-local",
                str(filepath_conda),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _logger.info(result_conda_install.stdout.decode(encoding))
        if result_conda_install.returncode != 0:
            _logger.warning(
                f"Failed to install conda package: {filepath_conda}"
            )
            _logger.error(result_conda_install.stderr.decode(encoding))
            list_filepaths_conda_failed.append(filepath_conda)

    # install pypi packages
    list_filepaths_pypi_failed: list[Path] = []
    for filepath_pypi in tqdm(
        tup_filepaths_pypi,
        desc="Installing PyPI packages",
        unit="package",
    ):
        result_pip_install = subprocess.run(
            [
                os.environ["CONDA_EXE"],
                "run",
                "-n",
                env_name,
                "pip",
                "install",
                "--no-deps",
                "--no-build-isolation",
                str(filepath_pypi),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _logger.info(result_pip_install.stdout.decode(encoding))
        if result_pip_install.returncode != 0:
            _logger.warning(f"Failed to install PyPI package: {filepath_pypi}")
            _logger.error(result_pip_install.stderr.decode(encoding))
            list_filepaths_pypi_failed.append(filepath_pypi)

    if list_filepaths_conda_failed:
        _logger.warning(
            f"Failed to install {len(list_filepaths_conda_failed)} conda packages."
        )
        for filepath in list_filepaths_conda_failed:
            _logger.warning(f"  - {filepath}")
    else:
        _logger.info("All conda packages installed successfully.")
    if list_filepaths_pypi_failed:
        _logger.warning(
            f"Failed to install {len(list_filepaths_pypi_failed)} PyPI packages."
        )
        for filepath in list_filepaths_pypi_failed:
            _logger.warning(f"  - {filepath}")
    else:
        _logger.info("All PyPI packages installed successfully.")

    _logger.info(
        f"Installed {len(tup_filepaths_conda) + len(tup_filepaths_pypi)} packages."
    )
    _logger.info(
        f"Failed to install {len(list_filepaths_conda_failed) + len(list_filepaths_pypi_failed)} packages."
    )
    if not list_filepaths_conda_failed and not list_filepaths_pypi_failed:
        _logger.info("All packages installed successfully.")
    else:
        _logger.warning(
            "Some packages failed to install. Please check the logs."
        )
