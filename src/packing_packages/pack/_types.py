"""Type definitions and utility functions for packages."""

import os
import re
from pathlib import Path
from typing import NamedTuple, Union

from packing_packages.constants import EXTENSIONS_CONDA, EXTENSIONS_PYPI


class Package(NamedTuple):
    """Package information.

    Parameters
    ----------
    name : str
        package name
    version : str
        package version
    build : str
        package build string
    channel : str
        package channel
    """

    name: str
    version: str
    build: str
    channel: str


def get_existing_packages_conda(
    dirpath_output: Union[os.PathLike, str],
) -> set[tuple[str, str, str]]:
    """get existing conda packages in the output directory

    Parameters
    ----------
    dirpath_output : str
        output directory path

    Returns
    -------
    set[tuple[str, str, str]]
        set of existing conda packages (name, version, build)
    """
    dirpath_output = Path(dirpath_output).resolve()

    st_packages_conda: set[tuple[str, str, str]] = set()
    for ext in EXTENSIONS_CONDA:
        for filepath_conda in dirpath_output.glob(f"**/*.{ext}"):
            if match := (
                re.match(rf"(.+)-(\d+.+?)-(.+)\.{ext}$", filepath_conda.name)
            ):
                package = Package(
                    name=match.group(1),
                    version=match.group(2),
                    build=match.group(3),
                    channel="",
                )
                st_packages_conda.add(package[:3])
    return st_packages_conda


def get_existing_packages_pypi(
    dirpath_output: Union[os.PathLike, str],
) -> set[tuple[str, str]]:
    """get existing pypi packages in the output directory

    Parameters
    ----------
    dirpath_output : str
        output directory path

    Returns
    -------
    set[tuple[str, str]]
        set of existing pypi packages (name, version)
    """
    dirpath_output = Path(dirpath_output).resolve()

    st_packages_pypi: set[tuple[str, str]] = set()
    for ext in EXTENSIONS_PYPI:
        for filepath_pypi in dirpath_output.glob(f"**/*.{ext}"):
            if match := re.match(
                rf"(.+)-(\d+.+?)-.+\.{ext}$", filepath_pypi.name
            ):
                package = Package(
                    name=match.group(1),
                    version=match.group(2),
                    build="",
                    channel="pypi",
                )
                st_packages_pypi.add((package.name, package.version))
                st_packages_pypi.add(
                    (package.name.replace("_", "-"), package.version)
                )
    return st_packages_pypi
