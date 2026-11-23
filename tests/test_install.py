"""End-to-end: create an env, pack it, install it with the generated script.

These tests create and remove conda environments, so they are meant for CI.
"""

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from packing_packages.pack import packing_packages
from packing_packages.scripts import generate_install_scripts

ENV_NAME_TARGET = "pp_test_target"
"""Environment to pack. It does not contain packing-packages itself."""

ENV_NAME_INSTALL = "pp_test_install"
"""Environment created by the generated install script."""

PYPI_PACKAGE = "six"
"""Small pure-Python package installed from PyPI into the target env."""

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"

pytestmark = pytest.mark.os_any


def _conda(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([os.environ["CONDA_EXE"], *args], check=True)


def _remove_env(env_name: str) -> None:
    subprocess.run(
        [os.environ["CONDA_EXE"], "env", "remove", "-y", "-n", env_name],
        check=False,
    )


@pytest.fixture(scope="module")
def env_target() -> Iterator[str]:
    _conda(
        "create",
        "-y",
        "-n",
        ENV_NAME_TARGET,
        "-c",
        "conda-forge",
        f"python={PYTHON_VERSION}",
        "pip",
    )
    _conda("run", "-n", ENV_NAME_TARGET, "pip", "install", PYPI_PACKAGE)
    yield ENV_NAME_TARGET
    _remove_env(ENV_NAME_TARGET)


@pytest.fixture
def env_install() -> Iterator[str]:
    _remove_env(ENV_NAME_INSTALL)
    yield ENV_NAME_INSTALL
    _remove_env(ENV_NAME_INSTALL)


def test_pack_and_install(env_target: str, env_install: str, tmp_path: Path):
    # strict: every package of the target env must be packed
    packing_packages(env_name=env_target, dirpath_target=tmp_path, strict=True)

    dirpath_packages = tmp_path / env_target
    filepath_bat = dirpath_packages / "install_packages.bat"
    filepath_sh = dirpath_packages / "install_packages.sh"

    # scripts are generated automatically after packing
    assert filepath_bat.is_file()
    assert filepath_sh.is_file()
    assert any((dirpath_packages / "pypi").glob(f"{PYPI_PACKAGE}-*"))

    # regenerate with another environment name to install into
    generate_install_scripts(
        dirpath_packages=dirpath_packages, env_name=env_install
    )

    if sys.platform.startswith("win"):
        subprocess.run(
            [str(filepath_bat)], check=True, stdin=subprocess.DEVNULL
        )
    else:
        subprocess.run(
            ["bash", str(filepath_sh)], check=True, stdin=subprocess.DEVNULL
        )

    _conda("run", "-n", env_install, "python", "-c", f"import {PYPI_PACKAGE}")
