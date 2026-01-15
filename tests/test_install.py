import os
import subprocess
import sys
from pathlib import Path

import pytest

from packing_packages.install import generate_install_scripts
from packing_packages.pack import packing_packages


@pytest.mark.os_windows
@pytest.mark.skipif(not sys.platform.startswith("win"), reason="Windows only")
def test_windows_specific():
    assert True


@pytest.mark.os_macos
@pytest.mark.skipif(not sys.platform.startswith("darwin"), reason="macOS only")
def test_macos_specific():
    assert True


@pytest.mark.os_win_mac
@pytest.mark.skipif(
    not sys.platform.startswith("darwin")
    and not sys.platform.startswith("win"),
    reason="macOS or Windows only",
)
def test_install():
    env_name_pack = os.environ["CONDA_DEFAULT_ENV"]
    env_name_create = "test_create"

    packing_packages(env_name=env_name_pack)

    dirpath_packages = Path(os.getcwd()).expanduser().resolve() / env_name_pack
    assert dirpath_packages.is_dir()

    generate_install_scripts(
        dirpath_packages=dirpath_packages, env_name=env_name_create
    )

    filepath_install_packages_bat = dirpath_packages / "install_packages.bat"
    filepath_install_packages_sh = dirpath_packages / "install_packages.sh"

    assert filepath_install_packages_bat.is_file()
    assert filepath_install_packages_sh.is_file()

    if sys.platform.startswith("win"):
        subprocess.run([str(filepath_install_packages_bat)], check=True)
    elif sys.platform.startswith("darwin"):
        subprocess.run([str(filepath_install_packages_sh)], check=True)
    else:
        raise ValueError(f"Unsupported platform: {sys.platform}")
