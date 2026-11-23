"""Unit tests that do not touch conda or the network."""

import subprocess
import sys
from pathlib import Path

import pytest

import packing_packages.helpers._helpers as helpers_mod
import packing_packages.install._core as install_core
import packing_packages.pack._utils as pack_utils
from packing_packages.__main__ import main
from packing_packages.helpers import (
    check_encoding,
    check_env_name,
    get_conda_sorted_packages_path,
    get_env_list,
    get_pypi_sorted_packages_path,
)
from packing_packages.install import install_packages
from packing_packages.pack._types import (
    Package,
    get_existing_packages_conda,
    get_existing_packages_pypi,
)
from packing_packages.pack._utils import (
    PackingError,
    _build_pip_command,
    _resolve_pypi_requirement,
    prepare_output_directory,
    raise_if_failed,
)

ENV_INFO = """\
# conda environments:
#
base                     /opt/conda
myenv                 *  /opt/conda/envs/myenv
"""


def _completed(
    returncode: int = 0, stdout: str = ""
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout.encode(), stderr=b"err"
    )


def _touch(dirpath: Path, *names: str) -> None:
    dirpath.mkdir(parents=True, exist_ok=True)
    for name in names:
        (dirpath / name).touch()


# --- helpers ---------------------------------------------------------------


def test_check_encoding():
    assert check_encoding("utf-8") == "utf-8"
    assert check_encoding(None) == sys.getdefaultencoding()
    with pytest.raises(ValueError, match="Invalid encoding"):
        check_encoding("no-such-encoding")


@pytest.fixture
def fake_env_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONDA_EXE", "conda")
    monkeypatch.setattr(
        helpers_mod.subprocess,
        "run",
        lambda *_, **__: _completed(stdout=ENV_INFO),
    )


def test_get_env_list(fake_env_list):
    assert get_env_list("utf-8") == {"base", "myenv"}


def test_check_env_name(fake_env_list, monkeypatch: pytest.MonkeyPatch):
    assert check_env_name("myenv", "utf-8") == "myenv"

    monkeypatch.setenv("CONDA_DEFAULT_ENV", "base")
    assert check_env_name(None, "utf-8") == "base"

    with pytest.raises(ValueError, match="'missing' not found"):
        check_env_name("missing", "utf-8")


def test_sorted_packages_path(tmp_path: Path):
    _touch(
        tmp_path / "conda",
        "zlib-1.3-h0_0.conda",
        "python-3.12.0-h0_0.tar.bz2",
        "abc-1.0-h0_0.conda",
    )
    _touch(
        tmp_path / "pypi",
        "requests-2.31.0-py3-none-any.whl",
        "setuptools-69.0-py3-none-any.whl",
        "pip-24.0.tar.gz",
    )

    assert [p.name for p in get_conda_sorted_packages_path(tmp_path)] == [
        "python-3.12.0-h0_0.tar.bz2",
        "abc-1.0-h0_0.conda",
        "zlib-1.3-h0_0.conda",
    ]
    assert [p.name for p in get_pypi_sorted_packages_path(tmp_path)] == [
        "pip-24.0.tar.gz",
        "setuptools-69.0-py3-none-any.whl",
        "requests-2.31.0-py3-none-any.whl",
    ]


# --- pack ------------------------------------------------------------------


def test_get_existing_packages(tmp_path: Path):
    _touch(tmp_path / "conda", "numpy-1.26.0-py312_0.conda")
    _touch(tmp_path / "pypi", "typing_extensions-4.9.0-py3-none-any.whl")

    assert get_existing_packages_conda(tmp_path) == {
        ("numpy", "1.26.0", "py312_0")
    }
    assert get_existing_packages_pypi(tmp_path) == {
        ("typing_extensions", "4.9.0"),
        ("typing-extensions", "4.9.0"),
    }


def test_prepare_output_directory_diff_only(tmp_path: Path):
    _touch(tmp_path / "myenv" / "conda", "numpy-1.26.0-py312_0.conda")

    dirpath_output, st_conda, st_pypi = prepare_output_directory(
        tmp_path, "myenv", diff_only=True, dry_run=False
    )

    assert dirpath_output.parent == tmp_path / "myenv" / "diffs"
    assert dirpath_output.is_dir()
    assert st_conda == {("numpy", "1.26.0", "py312_0")}
    assert st_pypi == set()


@pytest.mark.parametrize(
    ("version", "reachable", "expected"),
    [
        ("2.31.0", True, ("requests==2.31.0", None)),
        (
            "2.1.0+cu118",
            True,
            ("torch==2.1.0", "https://download.pytorch.org/whl/cu118"),
        ),
        ("2.1.0+cu118", False, ("torch==2.1.0+cu118", None)),
    ],
)
def test_resolve_pypi_requirement(
    monkeypatch: pytest.MonkeyPatch, version: str, reachable: bool, expected
):
    monkeypatch.setattr(pack_utils, "_is_valid_url", lambda _: reachable)
    name = "requests" if version == "2.31.0" else "torch"

    assert (
        _resolve_pypi_requirement(Package(name, version, "", "pypi"))
        == expected
    )


def test_build_pip_command(tmp_path: Path):
    cmd_download = _build_pip_command(
        "six==1.16.0", tmp_path, "3.12", False, "manylinux2014_x86_64", None
    )
    assert cmd_download[3:5] == ["download", "six==1.16.0"]
    assert ["-d", str(tmp_path)] == cmd_download[
        cmd_download.index("-d") : cmd_download.index("-d") + 2
    ]
    assert "manylinux2014_x86_64" in cmd_download

    cmd_dry_run = _build_pip_command(
        "six==1.16.0",
        tmp_path,
        "3.12",
        True,
        None,
        "https://example.com/simple",
    )
    assert cmd_dry_run[3] == "install"
    assert "--dry-run" in cmd_dry_run
    assert "--target" in cmd_dry_run
    assert "https://example.com/simple" in cmd_dry_run


def test_raise_if_failed():
    failed = [Package("numpy", "1.26.0", "py312_0", "conda-forge")]

    raise_if_failed([], strict=True)
    raise_if_failed(failed, strict=False)
    with pytest.raises(PackingError, match="numpy==1.26.0"):
        raise_if_failed(failed, strict=True)


# --- install ---------------------------------------------------------------


def test_install_packages_continues_on_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    _touch(
        tmp_path / "conda", "python-3.12.0-h0_0.conda", "bad-1.0-h0_0.conda"
    )
    _touch(tmp_path / "pypi", "six-1.16.0-py2.py3-none-any.whl")

    calls: list[list[str]] = []

    def fake_run(cmd, **_):
        calls.append(cmd)
        return _completed(returncode=1 if "bad" in cmd[-1] else 0)

    monkeypatch.setenv("CONDA_EXE", "conda")
    monkeypatch.setattr(
        install_core, "check_env_name", lambda env_name, _: env_name
    )
    monkeypatch.setattr(install_core.subprocess, "run", fake_run)

    install_packages(
        env_name="myenv", dirpath_packages=tmp_path, encoding="utf-8"
    )

    # every package is attempted even after a failure
    assert [Path(cmd[-1]).name for cmd in calls] == [
        "python-3.12.0-h0_0.conda",
        "bad-1.0-h0_0.conda",
        "six-1.16.0-py2.py3-none-any.whl",
    ]


# --- CLI -------------------------------------------------------------------


def test_cli_version(capsys: pytest.CaptureFixture):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"], prog="packing-packages")
    assert excinfo.value.code == 0
    assert "packing-packages" in capsys.readouterr().out


def test_cli_scripts(tmp_path: Path):
    _touch(tmp_path / "conda", "python-3.12.0-h0_0.conda")

    main(
        [
            "scripts",
            str(tmp_path),
            "-n",
            "myenv",
            "-e",
            "utf-8",
            "--no-create-env",
        ]
    )

    sh = (tmp_path / "install_packages.sh").read_text(encoding="utf-8")
    assert "env_name=myenv" in sh
    assert "conda create" not in sh
    assert (tmp_path / "install_packages.bat").is_file()


def test_cli_install_rejects_missing_dir(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        main(["install", str(tmp_path / "missing")])
