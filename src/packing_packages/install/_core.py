import os
import subprocess
from pathlib import Path, PureWindowsPath
from typing import Optional, Union

from packing_packages.constants import (
    EXTENSIONS_CONDA,
    EXTENSIONS_PYPI,
)
from packing_packages.helpers import (
    check_encoding,
    check_env_name,
    get_env_list,
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

MAX_LETTER_LENGTH_BAT = 7000
"""Maximum number of letters in a batch file.

'8192' is the maximum number of characters in a batch file.
But it is recommended to leave some margin for safety.
"""


def _get_conda_packages_path(
    dirpath_packages: Union[os.PathLike, str] = ".",
) -> tuple[Path, ...]:
    """Get paths of conda package files.

    Parameters
    ----------
    dirpath_packages : Union[os.PathLike, str], optional
        Directory path to search for conda packages, by default "."

    Returns
    -------
    tuple[Path, ...]
        Tuple of paths to conda package files
    """
    dirpath_packages = Path(dirpath_packages)

    return tuple(
        sum(
            [
                [
                    filepath
                    for filepath in dirpath_packages.glob(f"**/*{ext}")
                    if filepath.is_file()
                ]
                for ext in EXTENSIONS_CONDA
            ],
            start=[],
        )
    )


def _get_pypi_packages_path(
    dirpath_packages: Union[os.PathLike, str] = ".",
) -> tuple[Path, ...]:
    """Get paths of PyPI package files.

    Parameters
    ----------
    dirpath_packages : Union[os.PathLike, str], optional
        Directory path to search for PyPI packages, by default "."

    Returns
    -------
    tuple[Path, ...]
        Tuple of paths to PyPI package files
    """
    dirpath_packages = Path(dirpath_packages)

    return tuple(
        sum(
            [
                [
                    filepath
                    for filepath in dirpath_packages.glob(f"**/*{ext}")
                    if filepath.is_file()
                ]
                for ext in EXTENSIONS_PYPI
            ],
            start=[],
        )
    )


def _is_python_package(filepath: Path) -> bool:
    """Check if the package is a python package.

    Parameters
    ----------
    filepath : Path
        Path to the package file

    Returns
    -------
    bool
        True if the package name starts with "python-" or "python_", False otherwise
    """
    name_lower = filepath.name.lower()
    return name_lower.startswith("python-") or name_lower.startswith("python_")


def install_packages(
    env_name: Optional[str] = None,
    dirpath_packages: Union[str, os.PathLike] = ".",
    encoding: Optional[str] = None,
) -> None:
    """Install conda and PyPI packages.

    This function installs conda packages and PyPI packages from the specified
    directory into the specified conda environment. Conda packages are installed
    first, with Python packages prioritized. Failed installations are logged.

    Parameters
    ----------
    env_name : str, optional
        Conda environment name. If None, uses the current conda environment, by default None
    dirpath_packages : Union[str, os.PathLike], optional
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

    tup_filepaths_conda = _get_conda_packages_path(dirpath_packages)
    tup_filepaths_pypi = _get_pypi_packages_path(dirpath_packages)

    # Sort conda packages: python packages first
    tup_filepaths_conda = tuple(
        sorted(
            tup_filepaths_conda,
            key=lambda p: (not _is_python_package(p), p.name),
        )
    )

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


def generate_install_scripts(
    dirpath_packages: Union[str, os.PathLike] = ".",
    env_name: Optional[str] = None,
    output_dir: Optional[Union[str, os.PathLike]] = None,
    encoding: Optional[str] = None,
) -> dict[str, Path]:
    """Generate install scripts for Windows and Unix/Linux.

    This function generates install scripts that work on Windows (batch)
    and Unix/Linux (bash), avoiding wildcard expansion issues on Windows.
    The generated scripts do not depend on this package and can be distributed independently.

    Parameters
    ----------
    dirpath_packages : Union[str, os.PathLike], optional
        Directory path containing packages, by default "."
    env_name : str, optional
        Conda environment name. If None, uses directory name of dirpath_packages, by default None
    output_dir : Union[str, os.PathLike], optional
        Output directory for generated scripts. If None, uses dirpath_packages, by default None
    encoding : str, optional
        Encoding for generated script files. If None, uses system default encoding, by default None

    Returns
    -------
    dict[str, Path]
        Dictionary mapping script types to file paths:
        - "batch": Path to .bat file
        - "shell": Path to .sh file
    """
    dirpath_packages = Path(dirpath_packages).resolve()
    if not dirpath_packages.is_dir():
        raise FileNotFoundError(
            f"Package directory not found: {dirpath_packages}"
        )

    encoding = check_encoding(encoding)
    if env_name is None:
        env_name_list = get_env_list(encoding)
        if dirpath_packages.name in env_name_list:
            env_name = dirpath_packages.name
        else:
            raise ValueError(
                f"Environment '{dirpath_packages.name}' not found. (Directory name is automatically assigned as environment name.) "
                "Environments: ('{{}}')\n".format("','".join(env_name_list))
            )

    if output_dir is None:
        output_dir = dirpath_packages
    else:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

    # Find package files
    tup_filepaths_conda = _get_conda_packages_path(dirpath_packages)
    tup_filepaths_pypi = _get_pypi_packages_path(dirpath_packages)

    # Sort conda packages: python packages first
    tup_filepaths_conda_sorted = tuple(
        sorted(
            tup_filepaths_conda,
            key=lambda p: (not _is_python_package(p), p.name),
        )
    )

    # Generate Windows batch file (.bat)
    bat_content = [
        "@echo off",
        "setlocal enabledelayedexpansion",
        "",
        "REM Get the directory where this script is located",
        'set "SCRIPT_DIR=%~dp0"',
        "REM Remove trailing backslash for proper path concatenation",
        'if "!SCRIPT_DIR:~-1!"=="\\" set "SCRIPT_DIR=!SCRIPT_DIR:~0,-1!"',
        'cd /d "!SCRIPT_DIR!"',
        "",
        f"set env_name={env_name}",
        "",
        "REM Create new conda environment.",
        "call conda create -y -n %env_name% --offline --no-default-packages",
        "",
    ]
    if tup_filepaths_conda_sorted:
        bat_content.append("REM Install conda packages")

        tup_filepaths_conda_str = tuple(
            [
                "{}".format(
                    str(PureWindowsPath(filepath.relative_to(output_dir)))
                )
                for filepath in tup_filepaths_conda_sorted
            ]
        )
        n_str = sum(map(lambda x: len(x), tup_filepaths_conda_str))
        _logger.debug(f"'{n_str}' letters.")

        n_split = (n_str // MAX_LETTER_LENGTH_BAT) + bool(
            n_str % MAX_LETTER_LENGTH_BAT
        )
        n_packages = len(tup_filepaths_conda_str)
        n_packages_each_iter = n_packages // n_split + bool(
            n_packages % n_split
        )

        for i in range(n_split):
            bat_content.append(
                " ".join(
                    [
                        "call",
                        "conda",
                        "install",
                        "-y",
                        "-n",
                        "%env_name%",
                        "--offline",
                        "--use-local",
                    ]
                    + [
                        f"^\r\n    {filepath_str}"
                        for filepath_str in tup_filepaths_conda_str[
                            n_packages_each_iter * i : n_packages_each_iter
                            * (i + 1)
                        ]
                    ]
                )
            )
            bat_content.append("")

    if tup_filepaths_pypi:
        bat_content.append("REM Install PyPI packages")

        tup_filepaths_pypi_str = tuple(
            [
                "{}".format(
                    str(PureWindowsPath(filepath.relative_to(output_dir)))
                )
                for filepath in tup_filepaths_pypi
            ]
        )
        n_str = sum(map(lambda x: len(x), tup_filepaths_pypi_str))
        _logger.debug(f"'{n_str}' letters.")

        n_split = (n_str // MAX_LETTER_LENGTH_BAT) + bool(
            n_str % MAX_LETTER_LENGTH_BAT
        )
        n_packages = len(tup_filepaths_pypi_str)
        n_packages_each_iter = n_packages // n_split + bool(
            n_packages % n_split
        )

        for i in range(n_split):
            bat_content.append(
                " ".join(
                    [
                        "call",
                        "conda",
                        "run",
                        "-n",
                        "%env_name%",
                        "pip",
                        "install",
                        "--no-deps",
                        "--no-build-isolation",
                    ]
                    + [
                        f"^\r\n    {filepath_str}"
                        for filepath_str in tup_filepaths_pypi_str[
                            n_packages_each_iter * i : n_packages_each_iter
                            * (i + 1)
                        ]
                    ]
                )
            )
            bat_content.append("")

    bat_content.append("echo Installation completed.")
    bat_path = output_dir / "install_packages.bat"
    # Write .bat file with CRLF line endings
    bat_path.write_text("\r\n".join(bat_content), encoding=encoding)

    # Generate Unix/Linux shell script (.sh)
    sh_content = [
        "#!/bin/bash",
        "# Shell script to install packages",
        "",
        "set -e  # Exit on error",
        "",
        "# Get the directory where this script is located",
        'SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"',
        'cd "$SCRIPT_DIR"',
        "",
        f"env_name={env_name}",
        "# Create new conda environment.",
        "conda create -y -n $env_name --offline --no-default-packages",
        "",
    ]
    if tup_filepaths_conda_sorted:
        sh_content.append("# Install conda packages")
        sh_content.append(
            " ".join(
                [
                    "conda",
                    "install",
                    "-y",
                    "-n",
                    "$env_name",
                    "--offline",
                    "--use-local",
                ]
                + [
                    '\\\n    "{}"'.format(
                        filepath.relative_to(output_dir).as_posix()
                    )
                    for filepath in tup_filepaths_conda_sorted
                ]
            )
        )
        sh_content.append("")

    if tup_filepaths_pypi:
        sh_content.append("# Install PyPI packages")
        sh_content.append(
            " ".join(
                [
                    "conda",
                    "run",
                    "-n",
                    "$env_name",
                    "pip",
                    "install",
                    "--no-deps",
                    "--no-build-isolation",
                ]
                + [
                    '\\\n    "{}"'.format(
                        filepath.relative_to(output_dir).as_posix()
                    )
                    for filepath in tup_filepaths_pypi
                ]
            )
        )
        sh_content.append("")

    sh_content.append('echo "Installation completed."')
    sh_path = output_dir / "install_packages.sh"
    sh_content_str = "\n".join(sh_content)
    sh_path.write_text(sh_content_str, encoding="utf-8")

    # Make shell script executable on Unix systems
    try:
        os.chmod(sh_path, 0o755)
    except OSError:
        # Ignore on Windows
        pass

    _logger.info(
        "\n"
        f"Generated install scripts in '{output_dir}':\n"
        f"  - Windows batch: {bat_path}\n"
        f"  - Unix/Linux shell: {sh_path}\n"
    )

    return {
        "batch": bat_path,
        "shell": sh_path,
    }
