import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from shutil import copyfile
from typing import Literal, Optional, Union

from packing_packages.constants import EXTENSIONS_CONDA
from packing_packages.logging import get_child_logger
from packing_packages.pack._core import Package
from packing_packages.pack.yaml.constatns import PLATFORM_MAP
from packing_packages.utils import check_encoding, is_installed

if is_installed("tqdm"):
    from tqdm.auto import tqdm
else:
    from packing_packages.utils import (  # type: ignore[assignment]
        dummy_tqdm as tqdm,
    )


_logger = get_child_logger(__name__)


def packing_packages_from_yaml(*args, **kwargs):
    raise ModuleNotFoundError(
        "yaml has not found. You need to install pyyaml package."
    )


if is_installed("yaml"):
    import yaml

    def packing_packages_from_yaml(  # type: ignore[misc]
        filepath_yaml: Union[os.PathLike, str],
        *,
        platform: Optional[
            Literal[
                "win-64",
                "win-32",
                "linux-64",
                "linux-aarch64",
                "linux-ppc64le",
                "linux-s390x",
                "osx-64",
                "osx-arm64",
            ]
        ] = None,
        dirpath_target: Union[os.PathLike, str] = ".",
        dry_run: bool = False,
        encoding: Optional[str] = None,
    ) -> None:
        filepath_yaml = Path(filepath_yaml)
        encoding = check_encoding(encoding)

        if dry_run:
            _logger.warning("This is a dry run. No files will be downloaded.")

        if platform is None:
            platform_conda = None
            platform_pypi = None
            _logger.info(
                "Platform is not specified. "
                "The platform will be detected from the current environment."
            )
        else:
            platform_conda = PLATFORM_MAP[platform]["conda"]
            platform_pypi = PLATFORM_MAP[platform]["pypi"]

        # check install conda
        if "CONDA_EXE" not in os.environ:
            raise ValueError(
                "Please install conda and set the CONDA_EXE environment variable."
            )

        DIRPATH_CONDA_ROOT = Path(
            os.environ["CONDA_EXE"]
        ).parent.parent.resolve()
        dirpath_pkgs = DIRPATH_CONDA_ROOT / "pkgs"

        if not filepath_yaml.is_file():
            raise FileNotFoundError(filepath_yaml)
        with open(filepath_yaml, "r") as file:
            dict_yaml = yaml.safe_load(file)

        env_name = dict_yaml["name"]
        channels = dict_yaml["channels"]

        dirpath_target = Path(dirpath_target).resolve()
        if not dirpath_target.is_dir():
            raise FileNotFoundError(dirpath_target)

        dirpath_output = dirpath_target / env_name
        if not dry_run:
            os.makedirs(dirpath_output, exist_ok=True)
        _logger.info(f"Packing to '{dirpath_output}'...")

        dirpath_output_pypi = dirpath_output / "pypi"
        dirpath_output_conda = dirpath_output / "conda"
        for _dirpath in (dirpath_output_pypi, dirpath_output_conda):
            if not dry_run:
                os.makedirs(_dirpath, exist_ok=True)

        env_python_version: Optional[str] = None
        list_packages: list[Package] = list()
        for package_str in dict_yaml["dependencies"]:
            if isinstance(package_str, dict):
                for package_pypi in package_str["pip"]:
                    assert isinstance(package_pypi, str)
                    name, version = package_pypi.split("==")
                    list_packages.append(
                        Package(name, version, build="", channel="pypi")
                    )
            elif isinstance(package_str, str):
                name, version, build = package_str.split("=")
                list_packages.append(Package(name, version, build, ""))

                if name.lower() == "python":
                    env_python_version = version
            else:
                raise ValueError(package_str)

        assert env_python_version is not None, "Python has not found."

        # conda listで取得したpythonのバージョンと、現在のpythonのバージョンが異なる場合は警告を出す
        if (
            tuple(map(int, env_python_version.split(".")[:2]))
            != sys.version_info[:2]
        ):
            _logger.warning(
                "The Python version of the conda environment and the current Python version do not match. "
                "It is recommended to use the same Python version."
            )

        list_failed_packages: list[Package] = []
        for package in tqdm(list_packages):
            if package.channel == "pypi":
                if dry_run:
                    result_pip_download = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            f"{package.name}=={package.version}",
                            "--no-deps",
                            "--no-build-isolation",
                            "--python-version",
                            env_python_version,
                            "--dry-run",
                        ]
                        + (
                            ["--platform", platform_pypi]
                            if platform_pypi
                            else []
                        ),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                else:
                    result_pip_download = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "download",
                            f"{package.name}=={package.version}",
                            "--no-deps",
                            "--no-build-isolation",
                            "--python-version",
                            env_python_version,
                            "-d",
                            dirpath_output_pypi,
                        ]
                        + (
                            ["--platform", platform_pypi]
                            if platform_pypi
                            else []
                        ),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                _logger.info(
                    "\n" + result_pip_download.stdout.decode(encoding)
                )
                if result_pip_download.returncode != 0:
                    _logger.warning(f"'{package}' is not found.")
                    _logger.error(result_pip_download.stderr.decode(encoding))
                    list_failed_packages.append(package)
            else:
                # conda
                tup_filepaths_package = tuple(
                    dirpath_pkgs
                    / f"{package.name}-{package.version}-{package.build}.{ext}"
                    for ext in EXTENSIONS_CONDA
                )

                # あるときは、dirpath_pkgsからコピーする
                for filepath_package in tup_filepaths_package:
                    if filepath_package.is_file():
                        _logger.info(
                            f"Copying '{filepath_package.name}' from cache..."
                        )
                        if not dry_run:
                            copyfile(
                                filepath_package,
                                dirpath_output_conda / filepath_package.name,
                            )
                        break
                else:
                    _logger.info(
                        f"{package} is not found in the conda package cache."
                    )

                    # ない場合は、直接ダウンロード
                    result_conda_search = subprocess.run(
                        [
                            os.environ["CONDA_EXE"],
                            "search",
                            f"{package.name}={package.version}={package.build}",
                            "--info",
                        ]
                        + (
                            ["--platform", platform_conda]
                            if platform_conda
                            else []
                        )
                        + sum(
                            [["-c", channel] for channel in channels], start=[]
                        ),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    if match_conda_package_url := re.search(
                        r"url\s*:\s*(https?://\S+\.{})".format(
                            r"(?:"
                            + r"|".join(EXTENSIONS_CONDA).replace(r".", r"\.")
                            + r")"
                        ),
                        result_conda_search.stdout.decode(encoding),
                    ):
                        url = match_conda_package_url.group(1)
                    else:
                        _logger.warning(
                            "Could not detect the URL of the conda package."
                        )
                        continue

                    filename_download_conda = Path(url).name
                    _logger.info(
                        f"Downloading '{filename_download_conda}' from {url}"
                    )
                    if not dry_run:
                        try:
                            _ = urllib.request.urlretrieve(
                                url,
                                dirpath_output_conda / filename_download_conda,
                            )
                        except urllib.error.HTTPError as httperror:
                            _logger.exception(repr(httperror))
                            _logger.warning(
                                f"'{filename_download_conda}' could not be downloaded from {url}."
                            )
                            list_failed_packages.append(package)
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
        if n_failed > n_success:
            _logger.warning(
                "Failed over half of the packages. "
                "Please check the 'platform' option."
            )


if __name__ == "__main__":
    packing_packages_from_yaml(
        "./examples/torch311.yaml",
        platform="win-64",
    )
