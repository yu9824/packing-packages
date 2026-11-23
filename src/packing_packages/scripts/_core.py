"""Generate standalone install scripts (.bat / .sh) for packed packages."""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path, PureWindowsPath

from packing_packages.helpers import (
    PACKAGES_FOR_BUILD,
    check_encoding,
    get_conda_sorted_packages_path,
    get_env_list,
    get_pypi_sorted_packages_path,
)
from packing_packages.logging import get_child_logger

__all__ = ("generate_install_scripts",)

_logger = get_child_logger(__name__)

MAX_LETTER_LENGTH_BAT = 7000
"""Maximum number of letters in a batch file.

'8192' is the maximum number of characters in a batch file.
But it is recommended to leave some margin for safety.
"""


def split_pypi_packages_by_priority(
    packages_path: Sequence[Path],
) -> tuple[tuple[Path, ...], tuple[Path, ...]]:
    """Split PyPI package file paths by priority."""
    list_prior_packages: list[Path] = []

    for index_package in range(len(packages_path)):
        package_path = packages_path[index_package]
        package_path_stem = package_path.stem.replace("_", "-").lower()
        package_name = package_path_stem.split("-")[0]

        if package_name in PACKAGES_FOR_BUILD:
            list_prior_packages.append(package_path)
        else:
            break

    return (
        tuple(list_prior_packages),
        tuple(packages_path[index_package:]),
    )


def split_packages_path_for_bat(
    packages_path: Sequence[Path], output_dir: Path
) -> tuple[str, ...]:
    """

    Parameters
    ----------
    packages_path : Sequence[Path]
        _description_
    output_dir : Path
        _description_

    Returns
    -------
    tuple[str, ...]
        _description_
    """
    tup_filepaths_conda_str = tuple(
        [
            "{}".format(str(PureWindowsPath(filepath.relative_to(output_dir))))
            for filepath in packages_path
        ]
    )
    n_str = sum(map(lambda x: len(x), tup_filepaths_conda_str))
    _logger.debug(f"'{n_str}' letters.")

    n_split = (n_str // MAX_LETTER_LENGTH_BAT) + bool(
        n_str % MAX_LETTER_LENGTH_BAT
    )
    n_packages = len(tup_filepaths_conda_str)
    n_packages_each_iter = n_packages // n_split + bool(n_packages % n_split)

    return tuple(
        " ^\r\n    ".join(
            tup_filepaths_conda_str[
                n_packages_each_iter * i : n_packages_each_iter * (i + 1)
            ]
        )
        for i in range(n_split)
    )


def generate_install_scripts(
    dirpath_packages: str | os.PathLike = ".",
    env_name: str | None = None,
    output_dir: str | os.PathLike | None = None,
    encoding: str | None = None,
    create_env: bool = True,
) -> dict[str, Path]:
    """Generate install scripts for Windows and Unix/Linux.

    This function generates install scripts that work on Windows (batch)
    and Unix/Linux (bash), avoiding wildcard expansion issues on Windows.
    The generated scripts do not depend on this package and can be distributed independently.

    Parameters
    ----------
    dirpath_packages : str | os.PathLike, optional
        Directory path containing packages, by default "."
    env_name : str, optional
        Conda environment name. If None, uses directory name of dirpath_packages, by default None
    output_dir : str | os.PathLike, optional
        Output directory for generated scripts. If None, uses dirpath_packages, by default None
    encoding : str, optional
        Encoding for generated script files. If None, uses system default encoding, by default None
    create_env : bool, optional
        If True, the scripts create a new conda environment before installing.
        If False, packages are installed into an existing environment
        (e.g., for diff directories created by ``diff_only``), by default True

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
    tup_filepaths_conda = get_conda_sorted_packages_path(dirpath_packages)
    tup_filepaths_pypi = get_pypi_sorted_packages_path(dirpath_packages)
    tup_filepaths_pypi_prior, tup_filepaths_pypi_non_prior = (
        split_pypi_packages_by_priority(tup_filepaths_pypi)
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
    ]
    if create_env:
        bat_content.extend(
            [
                "REM Create new conda environment.",
                "call conda create -y -n %env_name% --offline --no-default-packages",
                "",
            ]
        )
    if tup_filepaths_conda:
        bat_content.append("REM Install conda packages")

        for filepath_str in split_packages_path_for_bat(
            tup_filepaths_conda, output_dir
        ):
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
                        f"^\r\n    {filepath_str}",
                    ]
                )
            )
            bat_content.append("")

    if tup_filepaths_pypi:
        bat_content.append("REM Install PyPI packages")

        for filepath_pypi_prior in tup_filepaths_pypi_prior:
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
                        str(
                            PureWindowsPath(
                                filepath_pypi_prior.relative_to(output_dir)
                            )
                        ),
                    ]
                )
            )
            bat_content.append("")

        for filepath_str in split_packages_path_for_bat(
            tup_filepaths_pypi_non_prior, output_dir
        ):
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
                        f"^\r\n    {filepath_str}",
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
    ]
    if create_env:
        sh_content.extend(
            [
                "# Create new conda environment.",
                "conda create -y -n $env_name --offline --no-default-packages",
                "",
            ]
        )
    if tup_filepaths_conda:
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
                    for filepath in tup_filepaths_conda
                ]
            )
        )
        sh_content.append("")

    if tup_filepaths_pypi:
        sh_content.append("# Install PyPI packages")
        for filepath_pypi_prior in tup_filepaths_pypi_prior:
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
                        filepath_pypi_prior.relative_to(output_dir).as_posix(),
                    ]
                )
            )
            sh_content.append("")

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
                    for filepath in tup_filepaths_pypi_non_prior
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
