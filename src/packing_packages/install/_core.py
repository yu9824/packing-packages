import os
import subprocess
from pathlib import Path
from typing import Optional, Union

from packing_packages.constants import (
    EXTENSIONS_CONDA,
    EXTENSIONS_PYPI,
)
from packing_packages.helpers import (
    check_encoding,
    check_env_name,
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


def _get_conda_packages_path(
    dirpath_packages: Union[os.PathLike, str] = ".",
) -> tuple[Path, ...]:
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
    """Check if the package is a python package."""
    name_lower = filepath.name.lower()
    return name_lower.startswith("python-") or name_lower.startswith("python_")


def install_packages(
    env_name: Optional[str] = None,
    dirpath_packages: Union[str, os.PathLike] = ".",
    encoding: Optional[str] = None,
) -> None:
    """install conda packages

    Parameters
    ----------
    env_name : str, optional
        conda environment name, by default None
    dirpath_packages : Union[str, os.PathLike], optional
        directory path of packages
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
    env_name = check_env_name(env_name, encoding=encoding)

    if output_dir is None:
        output_dir = dirpath_packages
    else:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

    # Find package files
    tup_filepaths_conda = _get_conda_packages_path(dirpath_packages)
    tup_filepaths_pypi = _get_pypi_packages_path(dirpath_packages)

    # Sort conda packages: python packages first
    tup_filepaths_conda_sorted = sorted(
        tup_filepaths_conda,
        key=lambda p: (not _is_python_package(p), p.name),
    )

    # Calculate relative paths from script location (output_dir) to packages
    def get_relative_path(filepath: Path) -> str:
        """Get relative path from output_dir to filepath using pathlib only."""
        output_dir_resolved = Path(output_dir).resolve()
        filepath_resolved = Path(filepath).resolve()
        try:
            rel_path = filepath_resolved.relative_to(output_dir_resolved)
            return rel_path.as_posix()
        except ValueError:
            # Fallback to absolute path if not under output_dir
            return filepath_resolved.as_posix()

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
    ]
    if tup_filepaths_conda_sorted:
        bat_content.append("REM Install conda packages")
        for filepath in tup_filepaths_conda_sorted:
            rel_path = get_relative_path(filepath)
            # Use backslashes for Windows batch file
            rel_path_windows = rel_path.replace("/", "\\")
            # Ensure backslash between SCRIPT_DIR and path
            bat_content.append(
                f'call conda install -y -n {env_name} --offline --use-local "!SCRIPT_DIR!\\{rel_path_windows}"'
            )
        bat_content.append("")
    if tup_filepaths_pypi:
        bat_content.append("REM Install PyPI packages")
        for filepath in tup_filepaths_pypi:
            rel_path = get_relative_path(filepath)
            # Use backslashes for Windows batch file
            rel_path_windows = rel_path.replace("/", "\\")
            # Ensure backslash between SCRIPT_DIR and path
            bat_content.append(
                f'call conda run -n {env_name} pip install --no-deps --no-build-isolation "!SCRIPT_DIR!\\{rel_path_windows}"'
            )
        bat_content.append("")
    bat_content.append("echo Installation completed.")
    bat_path = output_dir / "install_packages.bat"
    # Write .bat file with CRLF line endings
    bat_path.write_text("\r\n".join(bat_content), encoding="utf-8")

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
    ]
    if tup_filepaths_conda_sorted:
        sh_content.append("# Install conda packages")
        for filepath in tup_filepaths_conda_sorted:
            rel_path = get_relative_path(filepath)
            sh_content.append(
                f'conda install -y -n {env_name} --offline --use-local "$SCRIPT_DIR/{rel_path}"'
            )
        sh_content.append("")
    if tup_filepaths_pypi:
        sh_content.append("# Install PyPI packages")
        for filepath in tup_filepaths_pypi:
            rel_path = get_relative_path(filepath)
            sh_content.append(
                f'conda run -n {env_name} pip install --no-deps --no-build-isolation "$SCRIPT_DIR/{rel_path}"'
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

    _logger.info(f"Generated install scripts in '{output_dir}':")
    _logger.info(f"  - Windows batch: {bat_path}")
    _logger.info(f"  - Unix/Linux shell: {sh_path}")

    return {
        "batch": bat_path,
        "shell": sh_path,
    }
