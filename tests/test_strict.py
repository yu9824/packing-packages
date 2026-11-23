import subprocess
from pathlib import Path

import pytest

import packing_packages.pack._core as pack_core
from packing_packages.pack import PackingError, packing_packages
from packing_packages.pack.__main__ import main as main_pack

ENV_NAME = "dummy_env"

CONDA_LIST = """\
# packages in environment at /dummy/envs/dummy_env:
#
# Name                    Version                   Build  Channel
python                    3.12.0               h0_0    conda-forge
numpy                     1.26.0               py312_0    conda-forge
requests                  2.31.0               pypi_0    pypi
"""


@pytest.fixture
def fake_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Patch conda / download calls of ``packing_packages``.

    Returns a function to choose which package names fail to download.
    """
    failing: set[str] = set()

    monkeypatch.setenv("CONDA_EXE", "conda")
    monkeypatch.setattr(
        pack_core, "check_conda_installation", lambda: tmp_path
    )
    monkeypatch.setattr(
        pack_core, "check_env_name", lambda env_name, **_: env_name
    )
    monkeypatch.setattr(
        pack_core.subprocess,
        "run",
        lambda *_, **__: subprocess.CompletedProcess(
            args=[], returncode=0, stdout=CONDA_LIST.encode()
        ),
    )
    monkeypatch.setattr(
        pack_core,
        "download_pypi_package",
        lambda package, *_, **__: package.name not in failing,
    )
    monkeypatch.setattr(
        pack_core,
        "download_conda_package",
        lambda package, *_, **__: package.name not in failing,
    )

    def set_failing(*names: str) -> None:
        failing.clear()
        failing.update(names)

    return set_failing


def test_strict_raises_on_failure(fake_env, tmp_path: Path):
    fake_env("numpy", "requests")

    with pytest.raises(PackingError) as excinfo:
        packing_packages(
            env_name=ENV_NAME, dirpath_target=tmp_path, strict=True
        )

    assert {p.name for p in excinfo.value.failed_packages} == {
        "numpy",
        "requests",
    }
    assert "numpy==1.26.0" in str(excinfo.value)
    # scripts are not generated for an incomplete pack
    assert not (tmp_path / ENV_NAME / "install_packages.sh").exists()


def test_non_strict_does_not_raise(fake_env, tmp_path: Path):
    fake_env("numpy")

    packing_packages(env_name=ENV_NAME, dirpath_target=tmp_path, strict=False)

    assert (tmp_path / ENV_NAME / "install_packages.sh").is_file()


def test_strict_passes_without_failure(fake_env, tmp_path: Path):
    fake_env()

    packing_packages(env_name=ENV_NAME, dirpath_target=tmp_path, strict=True)

    assert (tmp_path / ENV_NAME / "install_packages.sh").is_file()


def test_cli_strict_exits_with_message(
    fake_env, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    fake_env("requests")
    monkeypatch.setattr(
        "packing_packages.pack.__main__.check_env_name",
        lambda env_name, **_: env_name,
    )

    with pytest.raises(SystemExit) as excinfo:
        main_pack(["-n", ENV_NAME, "-d", str(tmp_path), "--strict"])

    assert "requests==2.31.0" in str(excinfo.value.code)
