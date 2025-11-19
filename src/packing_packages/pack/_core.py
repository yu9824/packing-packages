import os
import subprocess
from pathlib import Path
from typing import Optional, Union

from packing_packages.helpers import check_encoding, is_installed
from packing_packages.logging import get_child_logger

from ._types import (
    Package,
    get_existing_packages_conda,
    get_existing_packages_pypi,
)
from ._utils import (
    check_conda_installation,
    check_python_version,
    download_conda_package,
    download_pypi_package,
    log_packing_results,
    prepare_output_directory,
)

if is_installed("tqdm"):
    from tqdm.auto import tqdm
else:
    from packing_packages.helpers import (  # type: ignore[assignment]
        dummy_tqdm as tqdm,
    )

# Re-export for backward compatibility
__all__ = (
    "Package",
    "get_existing_packages_conda",
    "get_existing_packages_pypi",
    "packing_packages",
)


_logger = get_child_logger(__name__)


def packing_packages(
    env_name: Optional[str] = None,
    dirpath_target: Union[os.PathLike, str] = ".",
    diff_only: bool = False,
    encoding: Optional[str] = None,
    dry_run: bool = False,
) -> None:
    """packaging conda environment packages

    Parameters
    ----------
    env_name : str
        conda environment name
    dirpath_target : str
        target directory path
    diff_only : bool
        if True, only download packages that are not already downloaded
    encoding : str
        encoding for subprocess output
    dry_run : bool
        if True, do not download files
    """

    encoding = check_encoding(encoding)

    if dry_run:
        _logger.warning("This is a dry run. No files will be downloaded.")

    dirpath_pkgs = check_conda_installation()

    if env_name is None:
        env_name = os.environ["CONDA_DEFAULT_ENV"]
    else:
        # check environment name
        result_conda_env_list = subprocess.run(
            [
                os.environ["CONDA_EXE"],
                "info",
                "-e",
            ],
            stdout=subprocess.PIPE,
        )
        conda_env_list = result_conda_env_list.stdout.decode(
            encoding
        ).splitlines()
        env_name_list = {
            line.split()[0]
            for line in conda_env_list
            if line and line[0] != "#"
        }
        if env_name not in env_name_list:
            raise ValueError(
                f"'{env_name}' is not found. Please check the environment name."
            )
    _logger.info(f"Packing conda environment '{env_name}'...")

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

    result_conda_list = subprocess.run(
        [
            os.environ["CONDA_EXE"],
            "list",
            "-n",
            env_name,
        ],
        stdout=subprocess.PIPE,
    )
    conda_list = result_conda_list.stdout.decode(encoding).splitlines()

    # conda listの出力をパースする
    list_packages: list[Package] = []
    for line in conda_list:
        if line[0] == "#":
            continue
        line_split = tuple(line.strip().split())
        package = Package(
            name=line_split[0],
            version=line_split[1],
            build=line_split[2],
            channel=line_split[3] if len(line_split) > 3 else "",
        )
        list_packages.append(package)
        if package.name == "python":
            env_python_version = package.version

    check_python_version(env_python_version)

    list_failed_packages: list[Package] = []
    for package in tqdm(list_packages):
        # pypiの場合はダウンロードする
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
            ):
                list_failed_packages.append(package)
            continue

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
        ):
            list_failed_packages.append(package)

    log_packing_results(list_packages, list_failed_packages)


if __name__ == "__main__":
    packing_packages("open-webui", "./open-webui")
