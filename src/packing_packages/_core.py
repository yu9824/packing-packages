import os
import subprocess
import sys
import warnings
from pathlib import Path
from shutil import copyfile
from typing import Optional, Union

DIRPATH_CONDA_ROOT = Path(
    os.environ.get("CONDA_ROOT", Path(os.environ["CONDA_EXE"]).parent.parent)
).resolve()
dirpath_pkgs = DIRPATH_CONDA_ROOT / "pkgs"

EXTENSIONS_CONDA = ("tar.bz2", "conda")


# TODO: 失敗したパッケージ名を保存しておく
# TODO: loggingする
# TODO: tqdmでプログレスバーを出しつつ、stdoutを非表示にする or loggingに流す。
# TODO: docstring作成
# pipでダウンロードする場合、同じバージョンのpythonじゃないとダウンロードできないことがある。同じ仮想環境でやるのがよさそう。
def packing_packages(
    env_name: Optional[str] = None,
    dirpath_output: Union[os.PathLike, str] = ".",
):
    dirpath_output = Path(dirpath_output).resolve()
    if not dirpath_output.is_dir():
        raise FileNotFoundError(dirpath_output)

    dirpath_output_pypi = dirpath_output / "pypi"
    dirpath_output_conda = dirpath_output / "conda"
    for _dirpath in (dirpath_output_pypi, dirpath_output_conda):
        os.makedirs(_dirpath, exist_ok=True)

    command_conda_list = "conda list" + (f" -n {env_name}" if env_name else "")
    conda_list = (
        subprocess.run(command_conda_list.split(), stdout=subprocess.PIPE)
        .stdout.decode("utf-8")
        .splitlines()
    )

    n_failed = 0
    n_success = 0
    for line in conda_list:
        if line[0] == "#":
            continue
        line_split = tuple(line.strip().split())
        package_name = line_split[0]
        package_version = line_split[1]
        package_build = line_split[2]
        channel = line_split[3] if len(line_split) > 3 else ""

        # pypiの場合はダウンロードする
        if channel == "pypi":
            result_pip_download = subprocess.run(
                f"{sys.executable} -m pip download {package_name}=={package_version} --no-deps -d {dirpath_output_pypi.as_posix()}".split()
            )
            if result_pip_download.returncode == 0:
                n_success += 1
            else:
                warnings.warn(f"{line} is not found.")
                n_failed += 1

            continue

        # condaの場合はすでにダウンロードされているやつから探す
        for ext in EXTENSIONS_CONDA:
            filename_package = (
                f"{package_name}-{package_version}-{package_build}.{ext}"
            )
            filepath_package = dirpath_pkgs / filename_package
            if filepath_package.is_file():
                copyfile(
                    filepath_package, dirpath_output_conda / filename_package
                )
                n_success += 1
                break
        else:
            warnings.warn(f"{line} is not found.")
            n_failed += 1
    print(f"{n_success} / {(n_success + n_failed)} packages are success!")


if __name__ == "__main__":
    packing_packages("open-webui", "./open-webui")
