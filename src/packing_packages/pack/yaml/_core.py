import os
from pathlib import Path
from typing import Literal, Optional, Union

from packing_packages.helpers import check_encoding, is_installed
from packing_packages.logging import get_child_logger
from packing_packages.pack._core import Package
from packing_packages.pack._utils import (
    check_conda_installation,
    check_python_version,
    download_conda_package,
    download_pypi_package,
    log_packing_results,
    prepare_output_directory,
)
from packing_packages.pack.yaml.constants import PLATFORM_MAP

if is_installed("tqdm"):
    from tqdm.auto import tqdm  # type: ignore
else:
    from packing_packages.helpers import (  # type: ignore[assignment]
        dummy_tqdm as tqdm,
    )


_logger = get_child_logger(__name__)


if is_installed("yaml"):
    import yaml  # type: ignore

    def packing_packages_from_yaml(
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
        diff_only: bool = False,
        dry_run: bool = False,
        encoding: Optional[str] = None,
    ) -> None:
        """Package Python dependencies from a YAML file for a specific platform.

        Parameters
        ----------
        filepath_yaml : str or os.PathLike
            Path to the YAML file containing package specifications.

        platform : {"win-64", "win-32", "linux-64", "linux-aarch64", "linux-ppc64le", "linux-s390x", "osx-64", "osx-arm64"}, optional
            Target platform for which packages should be downloaded. If None, the current platform is used.

        dirpath_target : str or os.PathLike, default="."
            Path to the directory where the downloaded package files will be saved.

        diff_only : bool, default=False
            If True, only download packages that are not already present in the target directory.

        dry_run : bool, default=False
            If True, simulate the download process without actually downloading any files.

        encoding : str, optional
            File encoding used to read the YAML file. If None, the system default encoding is used.

        Examples
        --------
        >>> packing_packages_from_yaml("env.yaml", platform="linux-64", dry_run=True)
        # Prints or logs the list of packages that would be downloaded for Linux 64-bit.

        >>> packing_packages_from_yaml("env.yaml", dirpath_target="./downloads")
        # Downloads packages into ./downloads based on the current platform.
        """

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

        dirpath_pkgs = check_conda_installation()

        if not filepath_yaml.is_file():
            raise FileNotFoundError(filepath_yaml)
        with open(filepath_yaml, "r") as file:
            dict_yaml = yaml.safe_load(file)

        env_name = Path(dict_yaml["name"]).name
        channels = dict_yaml["channels"]

        dirpath_output, st_existing_conda, st_existing_pypi = (
            prepare_output_directory(
                Path(dirpath_target),
                env_name,
                diff_only,
                dry_run,
            )
        )

        dirpath_output_pypi = dirpath_output / "pypi"
        dirpath_output_conda = dirpath_output / "conda"

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

        check_python_version(env_python_version)

        list_failed_packages: list[Package] = []
        for package in tqdm(list_packages):
            if package.channel == "pypi":
                if (package.name, package.version) in st_existing_pypi:
                    _logger.info(
                        f"'{package.name}=={package.version}' is already downloaded. Skipping..."
                    )
                    continue

                if not download_pypi_package(
                    package,
                    dirpath_output_pypi,
                    env_python_version,
                    encoding,
                    dry_run,
                    platform_pypi,
                ):
                    list_failed_packages.append(package)
            else:
                # conda
                if package[:3] in st_existing_conda:
                    _logger.info(
                        f"'{package.name}-{package.version}-{package.build}' is already downloaded. Skipping..."
                    )
                    continue

                if not download_conda_package(
                    package,
                    dirpath_pkgs,
                    dirpath_output_conda,
                    encoding,
                    dry_run,
                    platform_conda,
                    channels,
                ):
                    list_failed_packages.append(package)

        _, n_failed = log_packing_results(list_packages, list_failed_packages)
        n_success = len(list_packages) - n_failed
        if n_failed > n_success:
            _logger.warning(
                "Failed over half of the packages. "
                "Please check the 'platform' option."
            )
else:

    def packing_packages_from_yaml(*args, **kwargs):  # type: ignore[misc]
        raise ModuleNotFoundError(
            "yaml has not found. You need to install pyyaml package."
        )


if __name__ == "__main__":
    packing_packages_from_yaml(
        "./examples/torch311.yaml",
        platform="win-64",
    )
