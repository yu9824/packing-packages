"""Run the generated .bat against a stub conda.bat (Windows only)."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from packing_packages.scripts import generate_install_scripts

ENV_NAME = "dummy_env"

pytestmark = [
    pytest.mark.os_windows,
    pytest.mark.skipif(
        not sys.platform.startswith("win"), reason="Windows only"
    ),
]


def _generate_bat(dirpath: Path) -> Path:
    (dirpath / "conda").mkdir(parents=True)
    (dirpath / "conda" / "python-3.12.0-h0_0.conda").touch()
    return generate_install_scripts(
        dirpath, env_name=ENV_NAME, encoding="utf-8"
    )["batch"]


def _system_path() -> str:
    """PATH with only Windows system directories (no conda)."""
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    return os.pathsep.join([str(Path(system_root) / "System32"), system_root])


def _run_bat(
    filepath_bat: Path, path: str, answer: str
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["cmd", "/c", str(filepath_bat)],
        input=answer,
        text=True,
        capture_output=True,
        env={**os.environ, "PATH": path},
        timeout=60,
    )


@pytest.mark.parametrize(
    ("env_exists", "answer", "expect_create"),
    [
        (False, "", True),
        (True, "y\n", True),
        (True, "YES\n", True),
        (True, "n\n", False),
        (True, "\n", False),
        (True, "", False),  # EOF (non-interactive)
    ],
)
def test_bat_confirm_existing_env(
    tmp_path: Path, env_exists: bool, answer: str, expect_create: bool
):
    filepath_bat = _generate_bat(tmp_path / "packages")

    dirpath_bin = tmp_path / "bin"
    dirpath_bin.mkdir()
    filepath_log = tmp_path / "conda.log"
    (dirpath_bin / "conda.bat").write_text(
        "@echo off\r\n"
        f'echo %* >> "{filepath_log}"\r\n'
        f'if "%1"=="list" exit /b {0 if env_exists else 1}\r\n'
        "exit /b 0\r\n",
        encoding="utf-8",
    )

    result = _run_bat(
        filepath_bat,
        os.pathsep.join([str(dirpath_bin), _system_path()]),
        answer,
    )

    called = filepath_log.read_text(encoding="utf-8")
    assert ("create" in called) is expect_create, result.stdout
    assert (result.returncode == 0) is expect_create, result.stdout


def test_bat_conda_not_found(tmp_path: Path):
    filepath_bat = _generate_bat(tmp_path / "packages")

    result = _run_bat(filepath_bat, _system_path(), "")

    assert result.returncode == 1
    assert "'conda' command not found" in result.stdout
    assert "Miniforge Prompt" in result.stdout
