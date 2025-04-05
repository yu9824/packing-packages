import os
import subprocess
import sys
from pathlib import Path
from shutil import copyfile
from typing import NamedTuple, Optional, Union

from packing_packages.logging import get_child_logger
from packing_packages.utils import is_installed

if is_installed("tqdm"):
    from tqdm.auto import tqdm
else:
    from packing_packages.utils import (  # type: ignore[assignment]
        dummy_tqdm as tqdm,
    )

DIRPATH_CONDA_ROOT = Path(os.environ["CONDA_EXE"]).parent.parent.resolve()
dirpath_pkgs = DIRPATH_CONDA_ROOT / "pkgs"

EXTENSIONS_CONDA = ("tar.bz2", "conda")


class Package(NamedTuple):
    name: str
    version: str
    build: str
    channel: str


_logger = get_child_logger(__name__)


def packing_packages(
    env_name: Optional[str] = None,
    dirpath_target: Union[os.PathLike, str] = ".",
    dry_run: bool = False,
) -> None:
    """packaging conda environment packages

    packing_packages
    ----------
    env_name : str
        conda environment name
    dirpath_target : str
        target directory path
    dry_run : bool
        if True, do not download files
    """
    if dry_run:
        _logger.warning("This is a dry run. No files will be downloaded.")

    if env_name is None:
        env_name = os.environ["CONDA_DEFAULT_ENV"]

    dirpath_target = Path(dirpath_target).resolve()
    if not dirpath_target.is_dir():
        raise FileNotFoundError(dirpath_target)

    dirpath_output = dirpath_target / env_name
    os.makedirs(dirpath_output, exist_ok=True)

    dirpath_output_pypi = dirpath_output / "pypi"
    dirpath_output_conda = dirpath_output / "conda"
    for _dirpath in (dirpath_output_pypi, dirpath_output_conda):
        if not dry_run:
            os.makedirs(_dirpath, exist_ok=True)

    result_conda_list = subprocess.run(
        [
            os.environ["CONDA_EXE"],
            "list",
            "-n",
            env_name,
        ],
        stdout=subprocess.PIPE,
    )
    conda_list = result_conda_list.stdout.decode("utf-8").splitlines()

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

    # # conda listで取得したpythonのバージョンと、現在のpythonのバージョンが異なる場合は警告を出す
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
        # pypiの場合はダウンロードする
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
                        "--python-version",
                        f"{env_python_version}",
                        "--dry-run",
                        "--target",
                        dirpath_output_pypi.as_posix(),
                    ],
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
                        "--python-version",
                        f"{env_python_version}",
                        "-d",
                        dirpath_output_pypi.as_posix(),
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

            _logger.info("\n" + result_pip_download.stdout.decode("utf-8"))
            if result_pip_download.returncode != 0:
                _logger.warning(f"'{package}' is not found.")
                _logger.error(result_pip_download.stderr.decode("utf-8"))
                list_failed_packages.append(package)

            continue

        tup_filepaths_package = tuple(
            dirpath_pkgs
            / f"{package.name}-{package.version}-{package.build}.{ext}"
            for ext in EXTENSIONS_CONDA
        )
        # ないなら、conda installでダウンロードする
        if not any(
            filepath_package.is_file()
            for filepath_package in tup_filepaths_package
        ):
            result_conda_download = subprocess.run(
                [
                    os.environ["CONDA_EXE"],
                    "install",
                    "-y",
                    "-n",
                    env_name,
                    f"{package.name}={package.version}={package.build}",
                    "--no-deps",
                    "--download-only",
                ]
                + (["-c", package.channel] if package.channel else [])
                + (["--dry-run"] if dry_run else []),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _logger.info(result_conda_download.stdout.decode("utf-8"))
            if result_conda_download.returncode != 0:
                _logger.warning(f"'{package}' is not found.")
                _logger.error(result_conda_download.stderr.decode("utf-8"))
                list_failed_packages.append(package)
        else:
            for filepath_package in tup_filepaths_package:
                if filepath_package.is_file():
                    _logger.info(f"copying {filepath_package.name}")
                    if not dry_run:
                        copyfile(
                            filepath_package,
                            dirpath_output_conda / filepath_package.name,
                        )
                    break

    n_success = len(list_packages) - len(list_failed_packages)
    n_failed = len(list_failed_packages)
    _logger.info(
        f"{n_success} / {(n_success + n_failed)} packages are success!"
    )


if __name__ == "__main__":
    packing_packages("open-webui", "./open-webui")
