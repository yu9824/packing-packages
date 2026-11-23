"""Helpers to discover package files (conda / PyPI) in a directory."""

from __future__ import annotations

import os
from pathlib import Path

from packing_packages.constants import (
    EXTENSIONS_CONDA,
    EXTENSIONS_PYPI,
)

__all__ = (
    "PACKAGES_FOR_BUILD",
    "get_conda_sorted_packages_path",
    "get_pypi_sorted_packages_path",
)

PACKAGES_FOR_BUILD = (
    "python",
    "pip",
    "setuptools",
    "cython",
    "hatchling",
    "poetry",
)


def _get_conda_packages_path(
    dirpath_packages: os.PathLike | str = ".",
) -> tuple[Path, ...]:
    """Get paths of conda package files.

    Parameters
    ----------
    dirpath_packages : os.PathLike | str, optional
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
    dirpath_packages: os.PathLike | str = ".",
) -> tuple[Path, ...]:
    """Get paths of PyPI package files.

    Parameters
    ----------
    dirpath_packages : os.PathLike | str, optional
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


def _sort_packages_by_priority(
    filepaths: tuple[Path, ...],
) -> tuple[Path, ...]:
    """Sort package file paths by priority.

    Parameters
    ----------
    filepaths : tuple[Path, ...]
        Tuple of package file paths to sort

    Returns
    -------
    tuple[Path, ...]
        Tuple of package file paths sorted by priority
    """
    _priority = {name: i for i, name in enumerate(PACKAGES_FOR_BUILD)}
    return tuple(
        sorted(
            filepaths,
            key=lambda p: (
                _priority.get(
                    p.stem.replace("_", "-").lower().split("-")[0],
                    len(PACKAGES_FOR_BUILD),
                ),
                p.name,
            ),
        )
    )


def get_pypi_sorted_packages_path(
    dirpath_packages: os.PathLike | str = ".",
) -> tuple[Path, ...]:
    """Get paths of PyPI package files sorted by priority.

    Parameters
    ----------
    dirpath_packages : os.PathLike | str, optional
        Directory path to search for PyPI packages, by default "."

    Returns
    -------
    tuple[Path, ...]
        Tuple of paths to PyPI package files sorted by priority
    """
    filepaths_pypi = _get_pypi_packages_path(dirpath_packages)
    return _sort_packages_by_priority(filepaths_pypi)


def get_conda_sorted_packages_path(
    dirpath_packages: os.PathLike | str = ".",
) -> tuple[Path, ...]:
    """Get paths of conda package files sorted by priority.

    Parameters
    ----------
    dirpath_packages : os.PathLike | str, optional
        Directory path to search for conda packages, by default "."

    Returns
    -------
    tuple[Path, ...]
        Tuple of paths to conda package files sorted by priority
    """
    filepaths_conda = _get_conda_packages_path(dirpath_packages)
    return _sort_packages_by_priority(filepaths_conda)
